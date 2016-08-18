"NeoBundle Scripts-----------------------------
if &compatible
  set nocompatible               " Be iMproved
endif

" Required:
set runtimepath^=/home/hugh/.vim/bundle/neobundle.vim/

" Required:
call neobundle#begin(expand('/home/hugh/.vim/bundle'))

" Let NeoBundle manage NeoBundle
" Required:
NeoBundleFetch 'Shougo/neobundle.vim'

" Add or remove your Bundles here:
NeoBundle 'Shougo/neosnippet.vim'
NeoBundle 'Shougo/neosnippet-snippets'
NeoBundle 'tpope/vim-fugitive'
NeoBundle 'ctrlpvim/ctrlp.vim'
NeoBundle 'flazz/vim-colorschemes'
NeoBundle 'leafgarland/typescript-vim'
NeoBundle 'scrooloose/nerdcommenter'

" You can specify revision/branch/tag.
NeoBundle 'Shougo/vimshell', { 'rev' : '3787e5' }
NeoBundle 'Shougo/vimproc.vim', {'build' : {'linux' : 'make'}}
NeoBundle 'Quramy/tsuquyomi'
NeoBundle 'airblade/vim-gitgutter'

" Required:
call neobundle#end()

" Required:
filetype plugin indent on

" If there are uninstalled bundles found on startup,
" this will conveniently prompt you to install them.
NeoBundleCheck
"End NeoBundle Scripts-------------------------


" Global copy paste
vnoremap	<C-y>	"+yy
vnoremap	<C-v>	"+p


" Style goes here
set tabstop=2
set shiftwidth=2
syntax on
set backspace=2 " Makes backspace work like most apps
set number
