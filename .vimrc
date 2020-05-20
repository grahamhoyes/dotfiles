set autoindent
set tabstop=4
set shiftwidth=4
set expandtab
set number

" Set syntax hilighting
syntax on

" Editor color scheme
colo koehler

" Hilight search terms
set hlsearch

" Alt+h/l to move to left/right adjacent tab
execute "set <M-h>=\eh"
execute "set <m-l>=\el"
noremap <M-h> :tabprevious<CR>
noremap <M-l> :tabnext<CR>

noremap th :tabfirst<CR>
noremap tj :tabprev<CR>
noremap tk :tabnext<CR>
noremap tl :tablast<CR>

" Read .vimrc from project directories
set exrc
