# This is trash fire
find . -name "*.tar.gz" | awk '{l=$0; sub("\.tar\.gz", "", l); system("mkdir -p " l); print "tar -xf " $1, "-C", l "/"}' | sh
