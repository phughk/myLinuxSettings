## Additional env configuration
export GIT_EDITOR=vim
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"
export HISTTIMEFORMAT="%d/%m/%y %T "

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

## Functions that work like aliases
#docker() {
	#if [[$1 == "attach"]]; then
		#command docker attach --sig-proxy=true 
#}

## Update tmux git bar
~/.tmux-gitbar/update-gitbar

## Replace bash session with tmux (tmux autostart)
if [[ ! $TERM =~ screen ]]; then
	exec tmux attach
fi
