# Crafted manually by Graham Hoyes. Use `p10k configure` to build your own.
#
# Tip: Looking for a nice color? Here's a one-liner to print colormap.
#
#   for i in {0..255}; do print -Pn "%K{$i}  %k%F{$i}${(l:3::0:)i}%f " ${${(M)$((i%6)):#3}:+$'\n'}; done

# Temporarily change options.
'builtin' 'local' '-a' 'p10k_config_opts'
[[ ! -o 'aliases'         ]] || p10k_config_opts+=('aliases')
[[ ! -o 'sh_glob'         ]] || p10k_config_opts+=('sh_glob')
[[ ! -o 'no_brace_expand' ]] || p10k_config_opts+=('no_brace_expand')
'builtin' 'setopt' 'no_aliases' 'no_sh_glob' 'brace_expand'

() {
  emulate -L zsh -o extended_glob

  # Zsh >= 5.1 is required.
  [[ $ZSH_VERSION == (5.<1->*|<6->.*) ]] || return

  # Unset all configuration options. This allows you to apply configuration changes without
  # restarting zsh. Edit ~/.p10k.zsh and type `source ~/.p10k.zsh`.
  unset -m '(POWERLEVEL9K_*|DEFAULT_USER)~POWERLEVEL9K_GITSTATUS_DIR'

  export DEFAULT_USER="graham"

  typeset -g POWERLEVEL9K_MODE='nerdfont-complete'
  typeset -g POWERLEVEL9K_INSTANT_PROMPT="verbose"
  typeset -g POWERLEVEL9K_TRANSIENT_PROMPT="same-dir"

  typeset -g POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(virtualenv anaconda user ssh dir vcs status kubecontext)
  typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(root_indicator background_jobs)

  ## Python environments
  typeset -g POWERLEVEL9K_ANACONDA_LEFT_DELIMITER=""
  typeset -g POWERLEVEL9K_ANACONDA_RIGHT_DELIMITER=""
  typeset -g POWERLEVEL9K_VIRTUALENV_BACKGROUND='035'
  typeset -g POWERLEVEL9K_ANACONDA_BACKGROUND='035'
  typeset -g POWERLEVEL9K_ANACONDA_SHOW_PYTHON_VERSION=false
  typeset -g POWERLEVEL9K_ANACONDA_CONTENT_EXPANSION='${${CONDA_PROMPT_MODIFIER#\(}%\) }'

  ## dir
  typeset -g POWERLEVEL9K_DIR_PATH_SEPARATOR=" $(print_icon "LEFT_SUBSEGMENT_SEPARATOR") "
  typeset -g POWERLEVEL9K_DIR_HOME_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_HOME_FOREGROUND="255"
  typeset -g POWERLEVEL9K_HOME_SUB_ICON="$(print_icon 'HOME_ICON')"
  typeset -g POWERLEVEL9K_SHORTEN_DIR_LENGTH=2

  typeset -g POWERLEVEL9K_DIR_HOME_SUBFOLDER_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_HOME_SUBFOLDER_FOREGROUND="255"
  typeset -g POWERLEVEL9K_DIR_DEFAULT_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_DEFAULT_FOREGROUND="255"
  typeset -g POWERLEVEL9K_DIR_ETC_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_ETC_FOREGROUND="255"

  ## user
  typeset -g POWERLEVEL9K_HOME_FOLDER_ABBREVIATION=""
  typeset -g POWERLEVEL9K_USER_DEFAULT_BACKGROUND="242"
  typeset -g POWERLEVEL9K_USER_DEFAULT_FOREGROUND="255"

  ## vcs
  typeset -g POWERLEVEL9K_HIDE_BRANCH_ICON=true

  ## kubernetes
  typeset -g POWERLEVEL9K_KUBECONTEXT_SHOW_ON_COMMAND="kubectl|helm|kubens|kubectx|kk|k9s"
  typeset -g POWERLEVEL9K_KUBECONTEXT_SHOW_DEFAULT_NAMESPACE=0
  typeset -g POWERLEVEL9K_KUBECONTEXT_BACKGROUND=021
  # These docs will be helpful for deciphering the expansions below:
  # https://zsh.sourceforge.io/Doc/Release/Expansion.html#Parameter-Expansion
  # Display the project, zone, and cluster (if different from the zone) if using a cloud k8s context
  typeset -g POWERLEVEL9K_KUBECONTEXT_CONTENT_EXPANSION='${P9K_KUBECONTEXT_CLOUD_ACCOUNT:+${P9K_KUBECONTEXT_CLOUD_ACCOUNT} ${P9K_KUBECONTEXT_CLOUD_ZONE} ${${:-$P9K_KUBECONTEXT_CLOUD_CLUSTER}:#${P9K_KUBECONTEXT_CLOUD_ZONE}}}'
  # Display the full context name if using a non-cloud context
  POWERLEVEL9K_KUBECONTEXT_CONTENT_EXPANSION+='${${P9K_KUBECONTEXT_CLOUD_ACCOUNT:-${P9K_KUBECONTEXT_NAME}}:#${P9K_KUBECONTEXT_CLOUD_ACCOUNT}}'

  # If p10k is already loaded, reload configuration.
  # This works even with POWERLEVEL9K_DISABLE_HOT_RELOAD=true.
  (( ! $+functions[p10k] )) || p10k reload
}

# Tell `p10k configure` which file it should overwrite.
typeset -g POWERLEVEL9K_CONFIG_FILE=${${(%):-%x}:a}

(( ${#p10k_config_opts} )) && setopt ${p10k_config_opts[@]}
'builtin' 'unset' 'p10k_config_opts'
