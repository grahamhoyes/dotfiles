#!/usr/bin/python3

"""
Setup dotfiles and system configuration.

This script is broken into two sections:
    1. Install necessary tools and software
    2. Load configurations
"""

import argparse
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


def call(args, check=False, env=None):
    return run(args.strip().split(" "), check=check, env=env)


def clone(repo, destination="", args=""):
    if os.path.isdir(destination):
        raise FileExistsError(
            f"{destination} already exists. Did you mean to run with --update?"
        )

    call(f"git clone {repo} {destination} {args}")


class RunAndDone:
    """
    chdir into the specified directory, and return to the previous directory on exit
    """

    def __init__(self, path, create=True, purge=False):
        """
        :param path: Path to chdir into
        :param create: If True, create the directory before entering
        :param purge: If True, then the directory will be removed then re-created
        """
        self.path = path
        self.create = create
        self.purge = purge

    def __enter__(self):
        self.prev_path = os.getcwd()
        if self.purge and os.path.isdir(self.path):
            rmtree(path)

        if self.create and not os.path.isdir(self.path):
            os.makedirs(self.path)

        os.chdir(self.path)

    def __exit__(self, *args):
        os.chdir(self.prev_path)


call("sudo -v")


def first_install():
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
        "htop",
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
    print("Installing oh-my-zsh...")
    call(
        "curl -Lo oh-my-zsh_install.sh https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
    )
    call("sh oh-my-zsh_install.sh", env=dict(os.environ, CHSH="yes", RUNZSH="no"))
    os.remove("oh-my-zsh_install.sh")

    # Install powerlevel10k
    # This is my fork of powerlevel10k, which just tweaks how the base anaconda environment is shown
    # Note: I made a typo in "anaconda" when making the branch, fix that :facepalm:
    print("Installing powerlevel10k...")
    clone(
        "https://github.com/grahamhoyes/powerlevel10k.git",
        f"{HOME}/.oh-my-zsh/custom/themes/powerlevel10k",
        "-b base_anaconva_env --depth=1",
    )

    # Install zsh plugins
    print("Installing oh-my-zsh plugins...")
    clone(
        "https://github.com/zsh-users/zsh-syntax-highlighting.git",
        f"{HOME}/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
    )
    clone(
        "https://github.com/zsh-users/zsh-autosuggestions",
        f"{HOME}/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
    )

    # Install miniconda 3
    if os.path.isdir(f"{HOME}/.miniconda3"):
        raise FileExistsError(
            f"{HOME}.miniconda3/ already exists. Did you mean to run with --update?"
        )

    print("Installing miniconda3...")
    call(
        "curl -Lo miniconda3_install.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    )
    call(f"sh miniconda3_install.sh -p {HOME}/.miniconda3")
    os.remove("miniconda3_install.sh")

    # Some installers we want to stick around, specifically so we can update and rebuild when things go awry.
    # The `software` folder is in .gitignore and should be kept around
    with RunAndDone(f"{DOTFILES_DIR}/software", purge=True):
        # Install latte-dock, applets, and other tweaks
        print("Installing latte-dock...")
        # The latest git release of latte-dock doesn't work with window-appmenu,
        # so use the stable v9 version in the repositories for now
        call("sudo apt install -y latte-dock")

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

        clone("https://github.com/Zren/plasma-applet-eventcalendar.git")
        with RunAndDone("plasma-applet-eventcalendar"):
            call("kpackagetool5 -i package -t Plasma/Applet")


    # === Load and link configurations ===
    TARGET_DIR_TO_DOTFILES = {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".gitconfig"],
        f"{HOME}/.local/share/konsole": ["konsole.profile"],
        f"{HOME}/.config": ["kwinrc"],
    }

    for path, dotfiles in TARGET_DIR_TO_DOTFILES.items():
        with RunAndDone(path):
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

    print("Downloading fonts...")
    with RunAndDone(FONT_DIR):
        for font in fonts:
            url = f"https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/DejaVuSansMono/{font}"
            filename = font.split("/")[-1]
            res = requests.get(url)
            with open(filename, "wb+") as fd:
                fd.write(res.content)
        print("Updating font cache...")
        call(f"fc-cache -f")


def update():
    # === Update tools and software ===

    # Perform a system update
    call("sudo apt update")
    call("sudo apt dist-upgrade -y")

    # Update snaps
    call(f"sudo snap refresh")

    # Link desktop entries for snaps - this is necessary because krunner can't find them for some reason
    with RunAndDone(f"{HOME}/.local/share/applications"):
        for file in os.listdir("/var/lib/snapd/desktop/applications/"):
            if not file.endswith(".desktop"):
                continue
            call(f"ln -s /var/lib/snapd/desktop/applications/{file} .")

    # Update oh-my-zsh
    print("Updating oh-my-zsh...")
    with RunAndDone(f"{HOME}/.oh-my-zsh/", create=False):
        call("sh upgrade.sh")

    # Update powerlevel10k
    # This is my fork of powerlevel10k, which just tweaks how the base anaconda environment is shown
    # Note: I made a typo in "anaconda" when making the branch, fix that :facepalm:
    print("Updating powerlevel10k...")
    with RunAndDone(f"{HOME}/.oh-my-zsh/custom/themes/powerlevel10k/"):
        call("git pull origin base_anaconva_env")

    # Update zsh plugins
    print("Updating oh-my-zsh plugins...")
    with RunAndDone(
        f"{HOME}/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting", create=False
    ):
        call("git pull origin master")

    with RunAndDone(
        f"{HOME}/.oh-my-zsh/custom/plugins/zsh-autosuggestions", create=False
    ):
        call("git pull origin master")

    # Some installers we want to stick around, specifically so we can update and rebuild when things go awry.
    # The `software` folder is in .gitignore and should be kept around
    with RunAndDone(f"{DOTFILES_DIR}/software", create=False):
        # Install latte-dock, applets, and other tweaks
        print("Updating latte-dock...")
        # As long as latte-dock was installed with apt, it will
        # be updated above. When switching to the git version,
        # run install.sh again like below.

        with RunAndDone("applet-window-appmenu", create=False):
            call("git pull origin master")
            call("sh install.sh", check=True)

        with RunAndDone("applet-window-buttons", create=False):
            call("git pull origin master")
            call("sh install.sh", check=True)

        with RunAndDone("applet-window-title", create=False):
            call("git pull origin master")
            call("plasmapkg2 -i .")

        with RunAndDone("applet-latte-spacer", create=False):
            call("git pull origin master")
            call("plasmapkg2 -i .")

        with RunAndDone("latte-indicator-dashtopanel", create=False):
            call("git pull origin master")
            call("kpackagetool5 -i . -t Latte/Indicator")

        with RunAndDone("plasma-applet-presentwindows", create=False):
            call("git pull origin master")
            call("kpackagetool5 -i package -t Plasma/Applet")

        with RunAndDone("plasma-applet-eventcalendar"):
            call("git pull origin master")
            call("kpackagetool5 -i package -t Plasma/Applet")

    # === Load and link configurations ===
    TARGET_DIR_TO_DOTFILES = {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".gitconfig"],
        f"{HOME}/.local/share/konsole": ["konsole.profile"],
        f"{HOME}/.config": ["kwinrc"],
    }

    for path, dotfiles in TARGET_DIR_TO_DOTFILES.items():
        with RunAndDone(path):
            for dotfile in dotfiles:
                # Delete what's already there - this script should be ran before anything of
                # value is created
                if os.path.exists(dotfile) or os.path.islink(dotfile):
                    os.remove(dotfile)
                source = os.path.join(DOTFILES_DIR, dotfile)
                call(f"ln -s {source} {dotfile}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Bootstrap dotfiles and configuration")
    parser.add_argument(
        "--update",
        "-u",
        action="store_true",
        default=False,
        help="Update packages and configurations",
    )
    args = parser.parse_args()

    if args.update:
        update()
    else:
        first_install()
