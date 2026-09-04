#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

if [ "${1:-}" = "clean" ]; then
  if command -v latexmk >/dev/null 2>&1; then
    latexmk -C
  else
    find . -name '*.aux' -type f -delete
    rm -f main.bbl main.bcf main.blg main.fdb_latexmk main.fls main.lof main.log \
          main.lol main.lot main.out main.run.xml main.synctex.gz main.toc main.xdv main.pdf
  fi
  printf 'Clean completed.\n'
  exit 0
fi

if command -v latexmk >/dev/null 2>&1; then
  latexmk -xelatex main.tex
else
  xelatex -interaction=nonstopmode -halt-on-error main.tex
  biber main
  xelatex -interaction=nonstopmode -halt-on-error main.tex
  xelatex -interaction=nonstopmode -halt-on-error main.tex
fi

printf '\nBuild completed successfully: main.pdf\n'
