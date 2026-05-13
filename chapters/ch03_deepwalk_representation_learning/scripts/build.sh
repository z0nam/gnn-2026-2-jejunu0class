#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAPTER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SLIDES_DIR="$CHAPTER_DIR/slides"
NOTES_DIR="$CHAPTER_DIR/notes"
BUILD_DIR="$CHAPTER_DIR/build"
OUTPUT_DIR="$CHAPTER_DIR/output"

mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

compile_latex() {
  local workdir="$1"
  local input_tex="$2"
  (
    cd "$workdir"
    xelatex -interaction=nonstopmode -halt-on-error -output-directory "$BUILD_DIR" "$input_tex" >/dev/null
  )
}

compile_latex "$SLIDES_DIR" "ch03_beamer.tex"
compile_latex "$SLIDES_DIR" "ch03_handout.tex"
compile_latex "$SLIDES_DIR" "ch03_handout_text.tex"
compile_latex "$NOTES_DIR" "ch03_summary.tex"

cp -f "$BUILD_DIR/ch03_beamer.pdf" "$OUTPUT_DIR/ch03_beamer.pdf"
cp -f "$BUILD_DIR/ch03_handout.pdf" "$OUTPUT_DIR/ch03_handout.pdf"
cp -f "$BUILD_DIR/ch03_handout_text.pdf" "$OUTPUT_DIR/ch03_handout_text.pdf"
cp -f "$BUILD_DIR/ch03_summary.pdf" "$OUTPUT_DIR/ch03_summary.pdf"

echo "Build complete. PDFs are in: $OUTPUT_DIR"
