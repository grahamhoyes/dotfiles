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