#!/usr/bin/env bash

ROOT=`git rev-parse --show-toplevel`
DOCDIR="/tmp/pennmem.github.io"

echo "Removing old documentation directory"
rm -rf $DOCDIR

echo "Installing prerequisites"
cd $ROOT
python setup.py install
pip install -r requirements-docs.txt

echo "Building documentation..."
cd $ROOT/docs && make html
cd $ROOT/maint

echo "Cloning latest documentation..."
git clone git@github.com:pennmem/pennmem.github.io.git $DOCDIR

echo "Copying files..."
cp -R $ROOT/docs/_build/html/* $DOCDIR/ptsa

echo "Preparing to commit..."
cd $DOCDIR
read -p "Next you will be prompted to make a commit message... (press enter) "
git commit -a
echo "Don't forget to push with: cd $DOCDIR && git push"
