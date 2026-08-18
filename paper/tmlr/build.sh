#!/bin/zsh
# Build both flavors: main.pdf (anonymous submission) and preprint.pdf
# (named, real links). One source; the flavor pair is flipped by sed on
# a generated copy, never on main.tex itself.
set -e
export PATH="/Library/TeX/texbin:$PATH"
cd "${0:A:h}"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >/dev/null
sed -e 's/\\usepackage{tmlr}/\\usepackage[preprint]{tmlr}/' \
    -e 's/^\\anontrue$/\\anonfalse/' main.tex > preprint.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error preprint.tex >/dev/null
rm -f preprint.tex
echo "built: main.pdf (submission, anonymous) + preprint.pdf (named)"
