## Additional env configuration
export GIT_EDITOR=vim
export HISTTIMEFORMAT="%d/%m/%y %T "
export PATH=$(pwd)/bin:$PATH

## Prompt
RED="$(tput setaf 1)"
RESET="$(tput sgr0)"
export PS1='\[$RED\]$(echo $(dirname \w)|sed -e "s;\(/..\)[^/]*;\1;g")/$(basename \w)$ \[$RESET\]'

## Aliases
alias grep="grep --colour=always"
alias less="less -R"
alias sl="ls"
alias vimdiff="vim -d"

## Aliases for tools (scripts that need to be sourced)
alias mkcd="source $(which mkcd)"
alias cdls="source $(which cdls)"

binDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PATH=$binDir/bin:$PATH


## Update tmux git bar
#~/.tmux-gitbar/update-gitbar
#[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# Replace bash session with tmux (tmux autostart)
OSTYPE_MAC="darwin19"
if [$OSTYPE = $OSTYPE_MAC]; then
   if [[ ! $TERM =~ screen ]]; then
	exec tmux attach
   fi
fi

git config --global core.pager "less -FRX"

