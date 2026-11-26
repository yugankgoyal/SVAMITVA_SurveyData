#!/bin/sh
cd "$(dirname "$0")"
for f in fig_*.tex; do
  latexmk -pdf -interaction=nonstopmode "$f"
  mv "${f%.tex}.pdf" ../figures/
  latexmk -c "$f"
done
