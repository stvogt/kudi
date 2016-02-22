#! /bin/bash

# This install script works only for bash shell

USER=$(whoami)
BASHRC=~/.bashrc
PPATH="export PYTHONPATH=\$PYTHONPATH:$HOME/.kudi/src"
KPATH="export PATH=$HOME/.kudi/kScripts:\$PATH"

echo "installing python dependecies..."
sudo apt-get install python-numpy python-matplotlib python-scipy texlive texlive-latex-extra
echo "creating .kudi folder and finalizing the instalation, you can find the kudi scripts in $HOME/.kudi/kScripts/"

mkdir -p ~/.kudi/src/
mkdir -p ~/.kudi/kScripts/

cp ./src/*.py        $HOME/.kudi/src/
cp ./kScripts/*.py   $HOME/.kudi/kScripts/
cp ./preRun/*.py     $HOME/.kudi/kScripts/

echo "$PPATH" >> $BASHRC
echo "$KPATH" >> $BASHRC

source $HOME/.bashrc

