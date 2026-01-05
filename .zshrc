# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export PATH=$HOME/bin:/usr/local/bin:/snap/bin:$HOME/.local/bin:$HOME/.cargo/bin:/opt/homebrew/bin:$PATH

# Path to your oh-my-zsh installation.
export ZSH=$HOME/.oh-my-zsh

ZSH_THEME="powerlevel10k/powerlevel10k"

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

# This speeds up pasting with zsh-autosuggestions
# https://github.com/zsh-users/zsh-autosuggestions/issues/238
pasteinit() {
  OLD_SELF_INSERT=${${(s.:.)widgets[self-insert]}[2,3]}
  zle -N self-insert url-quote-magic
}

pastefinish() {
  zle -N self-insert $OLD_SELF_INSERT
}
zstyle :bracketed-paste-magic paste-init pasteinit
zstyle :bracketed-paste-magic paste-finish pastefinish

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

export EDITOR="vim"
# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi


# Aliases
alias rgrep="grep -n -r . -e"
alias kk="kubectx"
alias gpn="git push --no-verify"
alias ca="conda activate"
alias ce="conda deactivate"

# Activate a python virtual environment, switching out of a conda environment
# if necessary.
va() {
  local venv_dir
  if [ -d "venv" ]; then
    venv_dir="venv"
  elif [ -d ".venv" ]; then
    venv_dir=".venv"
  else
    echo "No virtual environment directory found"
    return 1
  fi

  conda deactivate 2>/dev/null || true
  source "$venv_dir/bin/activate"
}

# Deactivate a python virtual environment, switching back to the conda
# base environment.
vd() {
  if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
    conda activate 2>/dev/null || true
  elif [ -n "$CONDA_DEFAULT_ENV" ]; then
    conda deactivate
  else
    echo "No active virtual environment detected"
    return 1
  fi
}

alias ve="vd"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# === Setup for 3rd party software ===

## homebrew (linuxbrew when on linux)
if [ -f "/home/linuxbrew/.linuxbrew/bin/brew" ]; then eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv); fi

## (mini)conda
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

## cargo
if [ -f "$HOME/.cargo/env" ]; then . "$HOME/.cargo/env"; fi

## gcloud
export USE_GKE_GCLOUD_AUTH_PLUGIN=True

# The next line updates PATH for the Google Cloud SDK.
if [ -f "$HOME/bin/google-cloud-sdk/path.zsh.inc" ]; then . "$HOME/bin/google-cloud-sdk/path.zsh.inc"; fi

# The next line enables shell command completion for gcloud.
if [ -f "$HOME/bin/google-cloud-sdk/completion.zsh.inc" ]; then . "$HOME/bin/google-cloud-sdk/completion.zsh.inc"; fi

## nodenv
if [[ -d "$HOME/.nodenv/" ]]; then eval "$(nodenv init - --no-rehash zsh)"; fi
