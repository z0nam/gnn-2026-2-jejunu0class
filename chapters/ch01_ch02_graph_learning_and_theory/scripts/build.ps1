$ErrorActionPreference = "Stop"

$chapterDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$slidesDir = Join-Path $chapterDir "slides"
$notesDir = Join-Path $chapterDir "notes"
$buildDir = Join-Path $chapterDir "build"
$outputDir = Join-Path $chapterDir "output"

New-Item -ItemType Directory -Force $buildDir | Out-Null
New-Item -ItemType Directory -Force $outputDir | Out-Null

function Compile-Latex {
    param(
        [Parameter(Mandatory = $true)][string]$WorkingDir,
        [Parameter(Mandatory = $true)][string]$InputTex
    )

    Push-Location $WorkingDir
    try {
        & xelatex -interaction=nonstopmode -halt-on-error -output-directory $buildDir $InputTex | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "xelatex failed for $InputTex"
        }
    }
    finally {
        Pop-Location
    }
}

Compile-Latex -WorkingDir $slidesDir -InputTex "gnn_ch1_ch2_beamer.tex"
Compile-Latex -WorkingDir $slidesDir -InputTex "gnn_ch1_ch2_handout.tex"
Compile-Latex -WorkingDir $slidesDir -InputTex "gnn_ch1_ch2_handout_text.tex"
Compile-Latex -WorkingDir $notesDir -InputTex "hands_on_gnn_ch1_ch2_summary.tex"

Copy-Item -Force (Join-Path $buildDir "gnn_ch1_ch2_beamer.pdf") (Join-Path $outputDir "gnn_ch1_ch2_beamer.pdf")
Copy-Item -Force (Join-Path $buildDir "gnn_ch1_ch2_handout.pdf") (Join-Path $outputDir "gnn_ch1_ch2_handout.pdf")
Copy-Item -Force (Join-Path $buildDir "gnn_ch1_ch2_handout_text.pdf") (Join-Path $outputDir "gnn_ch1_ch2_handout_text.pdf")
Copy-Item -Force (Join-Path $buildDir "hands_on_gnn_ch1_ch2_summary.pdf") (Join-Path $outputDir "hands_on_gnn_ch1_ch2_summary.pdf")

Write-Output "Build complete. PDFs are in: $outputDir"
