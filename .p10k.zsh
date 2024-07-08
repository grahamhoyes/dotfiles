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

  typeset -g POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(
    # =========================[ Line #1 ]=========================
    virtualenv anaconda user ssh dir vcs status kubecontext
    # =========================[ Line #2 ]=========================
    newline
    prompt_char # Only visible for the current active prompt
    # All the following segments are only visible on already completed prompts
    command_execution_time
    status
  )

  typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
    # =========================[ Line #1 ]=========================
    time root_indicator background_jobs command_execution_time
    # =========================[ Line #2 ]=========================
    # These only appear on already completed prompts
    newline
    time
  )

  # Called right before rendering a prompt
  function p10k-on-pre-prompt()  { p10k display '1'=show '2/(right)'=hide '2/left/*'=hide '2/left/prompt_char'=show }
  # Called right before a prompt is retired
  function p10k-on-post-prompt() { p10k display '1'=hide '2/(right)'=show '2/left/*'=show '2/left/prompt_char'=hide }

  typeset -g POWERLEVEL9K_MODE='nerdfont-complete'
  typeset -g POWERLEVEL9K_INSTANT_PROMPT="verbose"
  typeset -g POWERLEVEL9K_TRANSIENT_PROMPT="off"
  # When set to `moderate`, some icons will have an extra space after them. This is meant to avoid
  # icon overlap when using non-monospace fonts. When set to `none`, spaces are not added.
  typeset -g POWERLEVEL9K_ICON_PADDING=none

  # Connect left prompt lines with these symbols. You'll probably want to use the same color
  # as POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_FOREGROUND below.
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_PREFIX= #'%244F╭─'
  typeset -g POWERLEVEL9K_MULTILINE_NEWLINE_PROMPT_PREFIX= #'%244F├─'
  typeset -g POWERLEVEL9K_MULTILINE_LAST_PROMPT_PREFIX= #'%244F╰─'
  # Connect right prompt lines with these symbols.
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_SUFFIX= #'%244F─╮'
  typeset -g POWERLEVEL9K_MULTILINE_NEWLINE_PROMPT_SUFFIX= #'%244F─┤'
  typeset -g POWERLEVEL9K_MULTILINE_LAST_PROMPT_SUFFIX= #'%244F─╯'

  # Add an empty line before each prompt.
  typeset -g POWERLEVEL9K_PROMPT_ADD_NEWLINE=true

  # Filler between left and right prompt on the first prompt line. You can set it to ' ', '·' or
  # '─'. The last two make it easier to see the alignment between left and right prompt and to
  # separate prompt from command output.
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_CHAR='─'
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_BACKGROUND=
  typeset -g POWERLEVEL9K_MULTILINE_NEWLINE_PROMPT_GAP_BACKGROUND=
  if [[ $POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_CHAR != ' ' ]]; then
    # The color of the filler. You'll probably want to match the color of POWERLEVEL9K_MULTILINE
    # ornaments defined above.
    typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_FOREGROUND=244
    # Start filler from the edge of the screen if there are no left segments on the first line.
    typeset -g POWERLEVEL9K_EMPTY_LINE_LEFT_PROMPT_FIRST_SEGMENT_END_SYMBOL='%{%}'
    # End filler on the edge of the screen if there are no right segments on the first line.
    typeset -g POWERLEVEL9K_EMPTY_LINE_RIGHT_PROMPT_FIRST_SEGMENT_START_SYMBOL='%{%}'
  fi

  ################################[ prompt_char: prompt symbol ]################################
    # Green prompt symbol if the last command succeeded.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND=76
  # Red prompt symbol if the last command failed.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND=196
  # Default prompt symbol.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VIINS_CONTENT_EXPANSION='❯'
  # Prompt symbol in command vi mode.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VICMD_CONTENT_EXPANSION='❮'
  # Prompt symbol in visual vi mode.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VIVIS_CONTENT_EXPANSION='V'
  # Prompt symbol in overwrite vi mode.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VIOWR_CONTENT_EXPANSION='▶'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_OVERWRITE_STATE=true
  # No line terminator if prompt_char is the last segment.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_LEFT_PROMPT_LAST_SEGMENT_END_SYMBOL=''
  # No line introducer if prompt_char is the first segment.
  typeset -g POWERLEVEL9K_PROMPT_CHAR_LEFT_PROMPT_FIRST_SEGMENT_START_SYMBOL=
  typeset -g POWERLEVEL9K_PROMPT_CHAR_LEFT_LEFT_WHITESPACE=
  typeset -g POWERLEVEL9K_PROMPT_CHAR_LEFT_RIGHT_WHITESPACE=
  typeset -g POWERLEVEL9K_PROMPT_CHAR_BACKGROUND="none"

  ####################################[ Python environments ]###################################
  typeset -g POWERLEVEL9K_ANACONDA_LEFT_DELIMITER=""
  typeset -g POWERLEVEL9K_ANACONDA_RIGHT_DELIMITER=""
  typeset -g POWERLEVEL9K_VIRTUALENV_BACKGROUND='035'
  typeset -g POWERLEVEL9K_ANACONDA_BACKGROUND='035'
  typeset -g POWERLEVEL9K_ANACONDA_SHOW_PYTHON_VERSION=false
  typeset -g POWERLEVEL9K_ANACONDA_CONTENT_EXPANSION='${${CONDA_PROMPT_MODIFIER#\(}%\) }'

  ##################################[ dir: current directory ]##################################
  typeset -g POWERLEVEL9K_DIR_PATH_SEPARATOR=" $(print_icon "LEFT_SUBSEGMENT_SEPARATOR") "
  typeset -g POWERLEVEL9K_DIR_HOME_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_HOME_FOREGROUND="255"
  typeset -g POWERLEVEL9K_HOME_SUB_ICON="$(print_icon 'HOME_ICON')"
  # Replace removed segment suffixes with this symbol.
  typeset -g POWERLEVEL9K_SHORTEN_DELIMITER="…"
  # Don't shorten directories that contain any of these files. They are anchors.
  local anchor_files=(
    .bzr
    .citc
    .git
    .hg
    .node-version
    .python-version
    .go-version
    .ruby-version
    .lua-version
    .java-version
    .perl-version
    .php-version
    .tool-versions
    .shorten_folder_marker
    .svn
    .terraform
    CVS
    Cargo.toml
    composer.json
    go.mod
    package.json
    stack.yaml
  )
  typeset -g POWERLEVEL9K_SHORTEN_FOLDER_MARKER="(${(j:|:)anchor_files})"
  # If directory is too long, shorten some of its segments to the shortest possible unique
  # prefix. The shortened directory can be tab-completed to the original.
  typeset -g POWERLEVEL9K_SHORTEN_STRATEGY=
  typeset -g POWERLEVEL9K_SHORTEN_DIR_LENGTH= #2

  typeset -g POWERLEVEL9K_DIR_HOME_SUBFOLDER_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_HOME_SUBFOLDER_FOREGROUND="255"
  typeset -g POWERLEVEL9K_DIR_DEFAULT_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_DEFAULT_FOREGROUND="255"
  typeset -g POWERLEVEL9K_DIR_ETC_BACKGROUND="031"
  typeset -g POWERLEVEL9K_DIR_ETC_FOREGROUND="255"

  ###########################################[ user ]###########################################
  typeset -g POWERLEVEL9K_HOME_FOLDER_ABBREVIATION=""
  typeset -g POWERLEVEL9K_USER_DEFAULT_BACKGROUND="242"
  typeset -g POWERLEVEL9K_USER_DEFAULT_FOREGROUND="255"

  #####################################[ vcs: git status ]######################################
  typeset -g POWERLEVEL9K_HIDE_BRANCH_ICON=true

  ########################################[ kubernetes ]########################################
  typeset -g POWERLEVEL9K_KUBECONTEXT_SHOW_ON_COMMAND="kubectl|helm|kubens|kubectx|kk|k9s"
  typeset -g POWERLEVEL9K_KUBECONTEXT_SHOW_DEFAULT_NAMESPACE=0
  typeset -g POWERLEVEL9K_KUBECONTEXT_BACKGROUND=021
  # These docs will be helpful for deciphering the expansions below:
  # https://zsh.sourceforge.io/Doc/Release/Expansion.html#Parameter-Expansion
  # Display the project, zone, and cluster (if different from the zone) if using a cloud k8s context
  typeset -g POWERLEVEL9K_KUBECONTEXT_CONTENT_EXPANSION='${P9K_KUBECONTEXT_CLOUD_ACCOUNT:+${P9K_KUBECONTEXT_CLOUD_ACCOUNT} ${P9K_KUBECONTEXT_CLOUD_ZONE} ${${:-$P9K_KUBECONTEXT_CLOUD_CLUSTER}:#${P9K_KUBECONTEXT_CLOUD_ZONE}}}'
  # Display the full context name if using a non-cloud context
  POWERLEVEL9K_KUBECONTEXT_CONTENT_EXPANSION+='${${P9K_KUBECONTEXT_CLOUD_ACCOUNT:-${P9K_KUBECONTEXT_NAME}}:#${P9K_KUBECONTEXT_CLOUD_ACCOUNT}}'

  ###################[ command_execution_time: duration of the last command ]###################
  # Execution time color.
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND=014
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_BACKGROUND=237
  # Show duration of the last command if takes at least this many seconds.
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_THRESHOLD=3
  # Show this many fractional digits. Zero means round to seconds.
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_PRECISION=0
  # Duration format: 1d 2h 3m 4s.
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_FORMAT='d h m s'

  ####################################[ time: current time ]####################################
  # Current time color.
  typeset -g POWERLEVEL9K_TIME_BACKGROUND=0
  typeset -g POWERLEVEL9K_TIME_FOREGROUND=66
  # Format for the current time: 09:51:02. See `man 3 strftime`.
  typeset -g POWERLEVEL9K_TIME_FORMAT='%D{%I:%M:%S %p}'
  # If set to true, time will update when you hit enter. This way prompts for the past
  # commands will contain the start times of their commands as opposed to the default
  # behavior where they contain the end times of their preceding commands.
  typeset -g POWERLEVEL9K_TIME_UPDATE_ON_COMMAND=true

  ##########################[ status: exit code of the last command ]###########################
  # Enable OK_PIPE, ERROR_PIPE and ERROR_SIGNAL status states to allow us to enable, disable and
  # style them independently from the regular OK and ERROR state.
  typeset -g POWERLEVEL9K_STATUS_EXTENDED_STATES=true

  # Status on success. No content, just an icon. No need to show it if prompt_char is enabled as
  # it will signify success by turning green.
  typeset -g POWERLEVEL9K_STATUS_OK=true
  typeset -g POWERLEVEL9K_STATUS_OK_BACKGROUND=0
  typeset -g POWERLEVEL9K_STATUS_OK_VISUAL_IDENTIFIER_EXPANSION='✔'

  # Status when some part of a pipe command fails but the overall exit status is zero. It may look
  # like this: 1|0.
  typeset -g POWERLEVEL9K_STATUS_OK_PIPE=true
  typeset -g POWERLEVEL9K_STATUS_OK_PIPE_VISUAL_IDENTIFIER_EXPANSION='✔'

  # Status when it's just an error code (e.g., '1'). No need to show it if prompt_char is enabled as
  # it will signify error by turning red.
  typeset -g POWERLEVEL9K_STATUS_ERROR=true
  typeset -g POWERLEVEL9K_STATUS_ERROR_VISUAL_IDENTIFIER_EXPANSION='✘'

  # Status when the last command was terminated by a signal.
  typeset -g POWERLEVEL9K_STATUS_ERROR_SIGNAL=true
  # Use terse signal names: "INT" instead of "SIGINT(2)".
  typeset -g POWERLEVEL9K_STATUS_VERBOSE_SIGNAME=false
  typeset -g POWERLEVEL9K_STATUS_ERROR_SIGNAL_VISUAL_IDENTIFIER_EXPANSION='✘'

  # Status when some part of a pipe command fails and the overall exit status is also non-zero.
  # It may look like this: 1|0.
  typeset -g POWERLEVEL9K_STATUS_ERROR_PIPE=true
  typeset -g POWERLEVEL9K_STATUS_ERROR_PIPE_VISUAL_IDENTIFIER_EXPANSION='✘'


  # If p10k is already loaded, reload configuration.
  # This works even with POWERLEVEL9K_DISABLE_HOT_RELOAD=true.
  (( ! $+functions[p10k] )) || p10k reload
}

# Tell `p10k configure` which file it should overwrite.
typeset -g POWERLEVEL9K_CONFIG_FILE=${${(%):-%x}:a}

(( ${#p10k_config_opts} )) && setopt ${p10k_config_opts[@]}
'builtin' 'unset' 'p10k_config_opts'
