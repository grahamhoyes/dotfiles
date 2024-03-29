# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:/usr/local/bin:/snap/bin:/home/graham/.local/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH=$HOME/.oh-my-zsh

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="powerlevel10k/powerlevel10k"

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Uncomment the following line to automatically update without prompting.
# DISABLE_UPDATE_PROMPT="true"

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS=true

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"


# Which plugins would you like to load?
# Standard plugins can be found in ~/.oh-my-zsh/plugins/*
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
    git
    docker
    docker-compose
    z
    zsh-syntax-highlighting
    zsh-autosuggestions
)


source $ZSH/oh-my-zsh.sh

# User configuration
CONDA_INSTALL_DIR="$HOME/.miniconda3"

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$("$CONDA_INSTALL_DIR/bin/conda" 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "$CONDA_INSTALL_DIR/etc/profile.d/conda.sh" ]; then
        . "$CONDA_INSTALL_DIR/etc/profile.d/conda.sh"
    else
        export PATH="$CONDA_INSTALL_DIR/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

## powerline configs
export DEFAULT_USER="graham"
POWERLEVEL9K_MODE='nerdfont-complete'

POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(virtualenv anaconda user ssh dir vcs status)
POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(root_indicator background_jobs)
POWERLEVEL9K_SHORTEN_DIR_LENGTH=2

# Python environments
POWERLEVEL9K_ANACONDA_LEFT_DELIMITER=""
POWERLEVEL9K_ANACONDA_RIGHT_DELIMITER=""
POWERLEVEL9K_VIRTUALENV_BACKGROUND='035'
POWERLEVEL9K_ANACONDA_BACKGROUND='035'
POWERLEVEL9K_ANACONDA_SHOW_PYTHON_VERSION=false
POWERLEVEL9K_ANACONDA_CONTENT_EXPANSION='${${CONDA_PROMPT_MODIFIER#\(}%\) }'

# dir
POWERLEVEL9K_DIR_PATH_SEPARATOR=" $(print_icon "LEFT_SUBSEGMENT_SEPARATOR") "
POWERLEVEL9K_DIR_HOME_BACKGROUND="031"
POWERLEVEL9K_DIR_HOME_FOREGROUND="255"
POWERLEVEL9K_HOME_SUB_ICON="$(print_icon 'HOME_ICON')"

POWERLEVEL9K_DIR_HOME_SUBFOLDER_BACKGROUND="031"
POWERLEVEL9K_DIR_HOME_SUBFOLDER_FOREGROUND="255"
POWERLEVEL9K_DIR_DEFAULT_BACKGROUND="031"
POWERLEVEL9K_DIR_DEFAULT_FOREGROUND="255"
POWERLEVEL9K_DIR_ETC_BACKGROUND="031"
POWERLEVEL9K_DIR_ETC_FOREGROUND="255"

# user
POWERLEVEL9K_HOME_FOLDER_ABBREVIATION=""
POWERLEVEL9K_USER_DEFAULT_BACKGROUND="242"
POWERLEVEL9K_USER_DEFAULT_FOREGROUND="255"

# vcs
POWERLEVEL9K_HIDE_BRANCH_ICON=true
#POWERLEVEL9K_VCS_GIT_ICON='\uE1AA'
#POWERLEVEL9K_VCS_GIT_GITHUB_ICON='\uE1AA'

# This speeds up pasting with zsh-autosuggestions
# https://github.com/zsh-users/zsh-autosuggestions/issues/238
pasteinit() {
  OLD_SELF_INSERT=${${(s.:.)widgets[self-insert]}[2,3]}
  zle -N self-insert url-quote-magic # I wonder if you'd need `.url-quote-magic`?
}

pastefinish() {
  zle -N self-insert $OLD_SELF_INSERT
}
zstyle :bracketed-paste-magic paste-init pasteinit
zstyle :bracketed-paste-magic paste-finish pastefinish

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"
alias rgrep="grep -n -r . -e"


. "$HOME/.cargo/env"
