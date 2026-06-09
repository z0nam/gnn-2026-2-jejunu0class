"""Generate runtime figures for ch10 presentation.

Outputs to ../slides/images/:
  ch10_runtime_vgae_ahat_heatmap.png   -- decoded adjacency on a small subgraph
  ch10_runtime_vgae_embedding_tsne.png -- 16-d VGAE embeddings -> 2D via t-SNE, colored by class
  ch10_runtime_drnl_example.png        -- one enclosing subgraph with DRNL labels
"""
from pathlib import Path
import numpy as np
import torch
import torch_geometric.transforms as T
from torch_geometric.datasets import Planetoid
from torch_geometric.nn import GCNConv, VGAE
from torch_geometric.utils import k_hop_subgraph, to_scipy_sparse_matrix
from scipy.sparse.csgraph import shortest_path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

torch.manual_seed(0); np.random.seed(0)
OUT = Path(__file__).resolve().parent.parent / "slides" / "images"
OUT.mkdir(parents=True, exist_ok=True)
device = torch.device("cpu")

# ---- VGAE part ---------------------------------------------------------------
transform = T.Compose([
    T.NormalizeFeatures(),
    T.ToDevice(device),
    T.RandomLinkSplit(num_val=0.05, num_test=0.1, is_undirected=True,
                      split_labels=True, add_negative_train_samples=False),
])
dataset = Planetoid(str(Path(__file__).resolve().parent), name="Cora", transform=transform)
train_data, val_data, test_data = dataset[0]

class Enc(torch.nn.Module):
    def __init__(self, din, dout):
        super().__init__()
        self.c1 = GCNConv(din, 2*dout)
        self.cmu = GCNConv(2*dout, dout)
        self.cs = GCNConv(2*dout, dout)
    def forward(self, x, ei):
        x = self.c1(x, ei).relu()
        return self.cmu(x, ei), self.cs(x, ei)

model = VGAE(Enc(dataset.num_features, 16)).to(device)
opt = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(301):
    model.train(); opt.zero_grad()
    z = model.encode(train_data.x, train_data.edge_index)
    loss = model.recon_loss(z, train_data.pos_edge_label_index) \
         + (1/train_data.num_nodes)*model.kl_loss()
    loss.backward(); opt.step()

with torch.no_grad():
    z = model.encode(test_data.x, test_data.edge_index)
    auc, ap = model.test(z, test_data.pos_edge_label_index,
                            test_data.neg_edge_label_index)
print(f"VGAE re-trained: AUC={auc:.4f} AP={ap:.4f}")

# ---- Fig: Ahat heatmap on a 30-node subset ----------------------------------
y = dataset[0][0].y  # original labels from before transform, but we have ys via test_data
# Use raw planetoid y
from torch_geometric.datasets import Planetoid as PL
raw = PL(str(Path(__file__).resolve().parent), name="Cora")
labels = raw.data.y.numpy()

# pick 30 nodes from 3 classes (10 each) to make pattern visible
classes = [0, 1, 2]
picked = []
for c in classes:
    idx = np.where(labels == c)[0][:10]
    picked.extend(idx.tolist())
picked = np.array(picked)

z_np = z.cpu().numpy()
A_sub = 1/(1+np.exp(-(z_np[picked] @ z_np[picked].T)))

fig, ax = plt.subplots(figsize=(5, 4.5))
im = ax.imshow(A_sub, cmap="viridis", vmin=0, vmax=1)
# class boundaries
for k in [10, 20]:
    ax.axhline(k-0.5, color="white", lw=1)
    ax.axvline(k-0.5, color="white", lw=1)
ax.set_xticks([4.5, 14.5, 24.5]); ax.set_xticklabels([f"class {c}" for c in classes])
ax.set_yticks([4.5, 14.5, 24.5]); ax.set_yticklabels([f"class {c}" for c in classes])
ax.set_title(r"$\hat{A} = \sigma(ZZ^\top)$ on 30 Cora nodes (10/class)")
plt.colorbar(im, ax=ax, fraction=0.046)
plt.tight_layout()
plt.savefig(OUT / "ch10_runtime_vgae_ahat_heatmap.png", dpi=150)
plt.close()
print("saved Ahat heatmap")

# ---- Fig: VGAE embedding t-SNE ----------------------------------------------
from sklearn.manifold import TSNE
emb2d = TSNE(n_components=2, perplexity=30, init="pca", random_state=0).fit_transform(z_np)

fig, ax = plt.subplots(figsize=(5.5, 4.5))
colors = plt.get_cmap("tab10")(labels / 7)
sc = ax.scatter(emb2d[:,0], emb2d[:,1], c=labels, cmap="tab10", s=6, alpha=0.7)
ax.set_title("VGAE node embeddings (t-SNE), Cora")
ax.set_xlabel("t-SNE-1"); ax.set_ylabel("t-SNE-2")
ax.legend(*sc.legend_elements(), title="class", loc="best", fontsize=8)
plt.tight_layout()
plt.savefig(OUT / "ch10_runtime_vgae_embedding_tsne.png", dpi=150)
plt.close()
print("saved t-SNE")

# ---- Fig: DRNL example on a real Cora enclosing subgraph --------------------
raw_data = raw.data
ei = raw_data.edge_index
# pick a positive edge where DRNL produces a varied label distribution
# (i.e., the enclosing subgraph stays connected even after removing the target link
# and has nodes at varying distances from both endpoints)
src_pick = dst_pick = None
best_variety = -1
for s, d in ei.t().tolist()[:5000]:
    sub_nodes, sub_ei, mapping, _ = k_hop_subgraph(
        [s, d], 2, ei, relabel_nodes=True)
    if not (8 <= sub_nodes.numel() <= 18):
        continue
    rs, rd = mapping.tolist()
    m1 = (sub_ei[0] != rs) | (sub_ei[1] != rd)
    m2 = (sub_ei[0] != rd) | (sub_ei[1] != rs)
    sub_ei_clean = sub_ei[:, m1 & m2]
    N_try = sub_nodes.size(0)
    adj_try = to_scipy_sparse_matrix(sub_ei_clean, num_nodes=N_try).tocsr()
    # paths from rs to rd without using the direct edge
    d_full = shortest_path(adj_try, directed=False, unweighted=True, indices=rs)
    if not np.isfinite(d_full[rd]):
        continue
    if d_full[rd] < 2:  # still have a direct alternate
        continue
    # count how many intermediate nodes are reachable from both endpoints
    d_from_d = shortest_path(adj_try, directed=False, unweighted=True, indices=rd)
    reachable_both = np.sum(np.isfinite(d_full) & np.isfinite(d_from_d)) - 2
    if reachable_both > best_variety:
        best_variety = reachable_both
        src_pick, dst_pick = s, d
        sub_nodes_keep, sub_ei_keep, mapping_keep = sub_nodes, sub_ei, mapping
        if reachable_both >= 5:
            break
assert src_pick is not None
print(f"picked edge ({src_pick},{dst_pick}); N={sub_nodes_keep.numel()} "
      f"reachable_both={best_variety}")

src, dst = mapping_keep.tolist()
# remove target edge
m1 = (sub_ei_keep[0] != src) | (sub_ei_keep[1] != dst)
m2 = (sub_ei_keep[0] != dst) | (sub_ei_keep[1] != src)
sub_ei_clean = sub_ei_keep[:, m1 & m2]
N = sub_nodes_keep.size(0)

src_o, dst_o = (dst, src) if src > dst else (src, dst)
adj = to_scipy_sparse_matrix(sub_ei_clean, num_nodes=N).tocsr()
idx = list(range(src_o)) + list(range(src_o+1, N))
adj_wo_src = adj[idx,:][:,idx]
idx2 = list(range(dst_o)) + list(range(dst_o+1, N))
adj_wo_dst = adj[idx2,:][:,idx2]
d_src = shortest_path(adj_wo_dst, directed=False, unweighted=True, indices=src_o)
d_src = np.insert(d_src, dst_o, 0)
d_dst = shortest_path(adj_wo_src, directed=False, unweighted=True, indices=dst_o-1)
d_dst = np.insert(d_dst, src_o, 0)
dist = d_src + d_dst
z_label = 1 + np.minimum(d_src, d_dst) + (dist//2)*(dist//2 + (dist%2) - 1)
z_label[src_o] = 1.0; z_label[dst_o] = 1.0
z_label[np.isnan(z_label) | np.isinf(z_label)] = 0
z_label = z_label.astype(int)

G = nx.Graph()
G.add_nodes_from(range(N))
G.add_edges_from(sub_ei_clean.t().tolist())
pos = nx.spring_layout(G, seed=0)

fig, ax = plt.subplots(figsize=(6.5, 4.8))
# color by DRNL label
node_colors = []
for i in range(N):
    if i == src_o or i == dst_o:
        node_colors.append("#d62728")  # target -- red
    elif z_label[i] == 0:
        node_colors.append("#aaaaaa")  # unreachable
    else:
        node_colors.append(plt.get_cmap("YlGnBu")(min(z_label[i]/8, 1.0)))
nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4)
# draw target edge as dashed red
ax.plot([pos[src_o][0], pos[dst_o][0]], [pos[src_o][1], pos[dst_o][1]],
        "r--", lw=2, alpha=0.7)
nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                       node_size=550, edgecolors="black")
labels_show = {i: f"z={z_label[i]}" for i in range(N)}
labels_show[src_o] = "u (z=1)"; labels_show[dst_o] = "v (z=1)"
nx.draw_networkx_labels(G, pos, labels=labels_show, ax=ax, font_size=7)
ax.set_title(f"DRNL labels on a Cora enclosing subgraph (k=2, N={N})\n"
             "red dashed = target link removed during training", fontsize=10)
ax.set_axis_off()
plt.tight_layout()
plt.savefig(OUT / "ch10_runtime_drnl_example.png", dpi=150)
plt.close()
print("saved DRNL example")
print("\nAll figures saved to", OUT)
