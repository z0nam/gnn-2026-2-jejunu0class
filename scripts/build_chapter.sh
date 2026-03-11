#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: ./scripts/build_chapter.sh <chapter_dir>"
  echo "Example: ./scripts/build_chapter.sh chapters/ch01_ch02_graph_learning_and_theory"
  exit 1
fi

CHAPTER_DIR="$1"
CHAPTER_SCRIPT="$CHAPTER_DIR/scripts/build.sh"

if [ ! -d "$CHAPTER_DIR" ]; then
  echo "Chapter directory not found: $CHAPTER_DIR"
  exit 1
fi

if [ ! -x "$CHAPTER_SCRIPT" ]; then
  if [ -f "$CHAPTER_SCRIPT" ]; then
    chmod +x "$CHAPTER_SCRIPT"
  else
    echo "Chapter build script not found: $CHAPTER_SCRIPT"
    exit 1
  fi
fi

"$CHAPTER_SCRIPT"
