## Additional env configuration
export PATH=$PATH:/home/hugh/opt/bin
export GIT_EDITOR=vim
export DOCKER_IP=127.0.0.1
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64/"

## Prompt
RED=$(tput setaf 1)
RESET=$(tput sgr0)
export PS1='$RED$(echo $(dirname \w)|sed -e "s;\(/..\)[^/]*;\1;g")/$(basename \w)$ $RESET'

## Aliases
alias grep="grep --colour=always"
alias less="less -R"
alias sl="ls"
alias vimdiff="vim -d"
