set number
set tabstop=4
set shiftwidth=4
set scrolloff=3
set smartindent
set noswapfile
set hlsearch
set belloff=all
nnoremap d "_d
vnoremap d "_d
colorscheme slate
let &t_ti.="\e[5 q"
hi MatchParen cterm=none ctermfg=250 ctermbg=55
hi Search ctermfg=250 ctermbg=55
nnoremap <ESC><ESC> :nohl<CR>
