## Additional software
export PATH=$PATH:/home/hugh/opt/bin

## Prompt
RED=$(tput setaf 1)
RESET=$(tput sgr0)
export PS1='$RED$(echo $(dirname \w)|sed -e "s;\(/..\)[^/]*;\1;g")/$(basename \w)$ $RESET'

## Aliases
alias grep="grep --colour=always"
alias less="less -R"
