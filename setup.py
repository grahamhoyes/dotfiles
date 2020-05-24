#!/usr/bin/python3

"""
Setup dotfiles and system configuration.

This script is broken into two sections:
    1. Install necessary tools and software
    2. Load configurations
"""

import os
import requests
from shutil import rmtree
from subprocess import run

# Make sure we're working from the right place
DOTFILES_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DOTFILES_DIR)

# getlogin() has caveats, but for running an install script it should suffice
USER = os.getlogin()
HOME = os.environ["HOME"]


def call(args, check=False):
    return run(args.strip().split(" "), check=check)


def clone(repo, destination=""):
    call(f"git clone {repo} {destination}")


def _make_and_chdir(path, purge=False):
    """
    Create the directory path if it does not already exist, then go there.

    If purge is True, then the directory will be deleted and re-created
    """
    if purge and os.path.isdir(path):
        rmtree(path)

    if not os.path.isdir(path):
        os.makedirs(path)
    os.chdir(path)


class RunAndDone:
    """
    chdir into the specified directory, and return to the previous directory on exit
    """

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.prev_path = os.getcwd()
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        os.chdir(self.path)

    def __exit__(self, *args):
        os.chdir(self.prev_path)


call("sudo -v")


# === Install tools and software ===
APT_TO_INSTALL = [
    "curl",
    "wget",
    "vim",
    "zsh",
    "cmake",
    "extra-cmake-modules",
    "qtdeclarative5-dev",
    "libqt5x11extras5-dev",
    "libkf5iconthemes-dev",
    "libkf5plasma-dev",
    "libkf5windowsystem-dev",
    "libkf5declarative-dev",
    "libkf5xmlgui-dev",
    "libkf5activities-dev",
    "build-essential",
    "libxcb-util-dev",
    "libkf5wayland-dev",
    "gettext",
    "libkf5archive-dev",
    "libkf5notifications-dev",
    "libxcb-util0-dev",
    "libsm-dev",
    "libkf5crash-dev",
    "libkf5newstuff-dev",
    "libxcb-randr0-dev",
    "libx11-xcb-dev",
    "libkdecorations2-dev",
]

SNAPS_TO_INSTALL = [
    "chromium",
    "slack --classic",
    "pycharm-professional --classic",
    "spotify",
]

# Add repos necessary for latte-dock
call("sudo add-apt-repository -y ppa:kubuntu-ppa/backports")
# Perform a system update
call("sudo apt update")
call("sudo apt dist-upgrade -y")

# Install apt packages
call("sudo apt install -y " + " ".join(APT_TO_INSTALL))

# Install snaps
for package in SNAPS_TO_INSTALL:
    call(f"sudo snap install {package}")

# Link desktop entries for snaps - this is necessary because krunner can't find them for some reason
with RunAndDone(f"{HOME}/.local/share/applications"):
    for file in os.listdir("/var/lib/snapd/desktop/applications/"):
        if not file.endswith(".desktop"):
            continue
        call(f"ln -s /var/lib/snapd/desktop/applications/{file} .")

# Install the latest version of oh-my-zsh the recommended way. This also sets the default shell to zsh.
call(
    "curl -Lo oh-my-zsh_install.sh https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
)
call("sh oh-my-zsh_install.sh")
os.remove("oh-my-zsh_install.sh")

# Install oh-my-zsh
# This is my fork of oh-my-zsh, which just tweaks how the base anaconda environment is shown
# Note: I made a typo in "anaconda" when making the branch, fix that :facepalm:
print("Installing oh-my-zsh...")
call(
    f"git clone -b base_anaconva_env --depth=1 https://github.com/grahamhoyes/powerlevel10k.git {HOME}/.oh-my-zsh/custom/themes/powerlevel10k"
)
# Install zsh plugins
print("Installing oh-my-zsh plugins...")
clone(
    "https://github.com/zsh-users/zsh-syntax-highlighting.git",
    "{HOME}/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
)
clone(
    "https://github.com/zsh-users/zsh-autosuggestions",
    "{HOME}/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
)

# Install miniconda 3
if not os.path.isdir(f"{HOME}/.miniconda3"):
    print("Installing miniconda3...")
    call(
        "curl -Lo miniconda3_install.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    )
    call(f"sh miniconda3_install.sh -p {HOME}/.miniconda3")
    os.remove("miniconda3_install.sh")
else:
    print("Skipping miniconda3 install")

# Some installers we want to stick around, specifically so we can update and rebuild when things go awry.
# The `software` folder is in .gitignore and should be kept around
_make_and_chdir(f"{DOTFILES_DIR}/software", purge=True)

# Install latte-dock, applets, and other tweaks
print("Installing latte-dock...")
clone("https://github.com/KDE/latte-dock.git")
with RunAndDone("latte-dock"):
    call("sh install.sh", check=True)

clone("https://github.com/psifidotos/applet-window-appmenu.git")
with RunAndDone("applet-window-appmenu"):
    call("sh install.sh", check=True)

clone("https://github.com/psifidotos/applet-window-buttons.git")
with RunAndDone("applet-window-buttons"):
    call("sh install.sh", check=True)

clone("https://github.com/psifidotos/applet-window-title")
with RunAndDone("applet-window-title"):
    call("plasmapkg2 -i .")

clone("https://github.com/psifidotos/applet-latte-spacer/")
with RunAndDone("applet-latte-spacer"):
    call("plasmapkg2 -i .")

clone("https://github.com/psifidotos/latte-indicator-dashtopanel.git")
with RunAndDone("latte-indicator-dashtopanel"):
    call("kpackagetool5 -i . -t Latte/Indicator")

clone("https://github.com/Zren/plasma-applet-presentwindows.git")
with RunAndDone("plasma-applet-presentwindows"):
    call("kpackagetool5 -i package -t Plasma/Applet")

# === Load and link configurations ===
TARGET_DIR_TO_DOTFILES = {
    HOME: [".vimrc", ".tmux.conf", ".zshrc", ".gitconfig"],
    f"{HOME}/.local/share/konsole": ["konsole.profile"],
    f"{HOME}/.config": ["kwinrc"],
}

for path, dotfiles in TARGET_DIR_TO_DOTFILES.items():
    _make_and_chdir(path)
    for dotfile in dotfiles:
        # Delete what's already there - this script should be ran before anything of
        # value is created
        if os.path.exists(dotfile) or os.path.islink(dotfile):
            os.remove(dotfile)
        source = os.path.join(DOTFILES_DIR, dotfile)
        call(f"ln -s {source} {dotfile}")

# Install the desired nerdfont
FONT_DIR = os.path.join(HOME, ".local/share/fonts")
fonts = [
    "Bold/complete/DejaVu Sans Mono Bold Nerd Font Complete Mono.ttf",
    "Bold-Italic/complete/DejaVu Sans Mono Bold Oblique Nerd Font Complete Mono.ttf",
    "Italic/complete/DejaVu Sans Mono Oblique Nerd Font Complete Mono.ttf",
    "Regular/complete/DejaVu Sans Mono Nerd Font Complete Mono.ttf",
]

_make_and_chdir(FONT_DIR)

print("Downloading fonts...")
for font in fonts:
    url = f"https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/DejaVuSansMono/{font}"
    filename = font.split("/")[-1]
    res = requests.get(url)
    with open(filename, "wb+") as fd:
        fd.write(res.content)
print("Updating font cache...")
call(f"fc-cache -f")
