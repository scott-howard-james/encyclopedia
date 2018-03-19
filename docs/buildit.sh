make html
pandoc -s -f markdown -t rst brieftour.md -o brieftour.rst
pandoc -s -f markdown -t rst examples.md -o examples.rst
