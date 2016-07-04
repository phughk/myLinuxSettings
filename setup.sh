#!/bin/sh

# Attach bashrc
echo "### EDITED" >> ~/.bashrc
echo "source $(pwd)/bashrc" >> ~/.bashrc

# Attach vimrc
echo "so $(pwd)/vimrc" >> ~/.vimrc

# Attach tmux
echo "source-file $(pwd)/tmux.conf" >> ~/.tmux.conf
