#!/usr/bin/env python3

"""
Setup dotfiles and system configuration.

This script is broken into two sections:
    1. Install necessary tools and software
    2. Load configurations
"""

import argparse
from cmath import e
import os
import platform
import requests
from shutil import rmtree
from subprocess import run
import sys

os_name = platform.system()
arch = platform.machine()

if os_name not in ("Linux", "Darwin"):
    print(f"{os_name} is not a supported environment")
    sys.exit(1)

if arch not in ("x86_64"):
    print(f"{arch} is not a supported architecture")
    sys.exit(1)


# Make sure we're working from the right place
DOTFILES_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DOTFILES_DIR)

# getlogin() has caveats, but for running an install script it should suffice
USER = os.getlogin()
HOME = os.environ["HOME"]

# For each supported OS, map destination locations
# to dotfiles that should be linked there
DOTFILE_LOCATIONS = {
    "Linux": {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".gitconfig"],
        f"{HOME}/.local/share/konsole": ["konsole.profile"],
        f"{HOME}/.config": ["kwinrc"],
        #f"{HOME}/.config/latte": ["Condensed.layout.latte"], # Must be imported manually
    },
    "Darwin": {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".gitconfig"],
    }
}

_is_sudo = False
def sudo():
    global _is_sudo

    if _is_sudo:
        return

    call("sudo -v")

    _is_sudo = True

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


def link_configs(overwrite=False):
    configs = DOTFILE_LOCATIONS[os_name]

    for path, dotfiles in configs.items():
        with RunAndDone(path):
            for dotfile in dotfiles:
                if os.path.exists(dotfile) or os.path.islink(dotfile):
                    if overwrite:
                        os.remove(dotfile)
                    else:
                        continue

                source = os.path.join(DOTFILES_DIR, dotfile)
                call(f"ln -s {source} {dotfile}")


call("sudo -v")

_setup_shell_unix_done = False

def setup_shell_unix():
    """
    Sets up my preferred shell with Oh My Zsh, Powerlevel10k,
    and miniconda on any Mac or Linux machine.

    This assumes that zsh is already installed.

    Does not require privileged execution, so this can be executed
    anywhere.
    """

    global _setup_shell_unix_done

    if _setup_shell_unix_done:
        # Only run once
        return

    # Install the latest version of Oh My Zsh the recommended way.
    # This also sets the default shell to zsh if possible (if not,
    # you may need to set it manually).
    print("Installing Oh My Zsh...")
    call(
        "curl -Lo oh-my-zsh_install.sh https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
    )
    call("sh oh-my-zsh_install.sh", env={
        **os.environ,
        "CHSH": "yes",
        "RUNZSH": "no"
    })
    os.remove("oh-my-zsh_install.sh")

    # Install Powerlevel10k
    print("Installing powerlevel10k...")
    clone(
        "https://github.com/romkatv/powerlevel10k.git",
        f"{HOME}/.oh-my-zsh/custom/themes/powerlevel10k"
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

    # Install Miniconda 3
    #
    # Running the installer with -b will install in silent mode,
    # and not initialize the shell. The .zshrc file in this repo
    # already has the `conda init zsh` output in it.
    print("Installing Miniconda")
    if os.path.isdir("f{HOME}/.miniconda3"):
        print(f"{HOME}/.miniconda3/ already exists. Skipping install")
    else:
        if os_name == "Linux":
            miniconda_installer = "https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh"
        elif os_name == "Darwin":
            # Apple silicon not supported (until I get one)
            miniconda_installer = "https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-MacOSX-x86_64.sh"

        call(f"curl -Lo miniconda3_install.sh {miniconda_installer}")
        call(f"sh miniconda3_install.sh -b -p ${HOME}/.miniconda3")
        os.remove("miniconda3_install.sh")

    _setup_shell_unix_done = True

_install_fonts_done = False

def install_fonts():
    """
    Installs terminal fonts on Mac on Linux.

    This does not need to be run on remote machines, only clients.

    Fonts to install:
        - DejaVu Sans Mono
    """

    global _install_fonts_done

    if _install_fonts_done:
        # Only run once
        return

    if os_name == "Linux":
        font_dir = f"{HOME}/.local/share/fonts"
    elif os_name == "Darwin":
        font_dir = f"{HOME}/Library/Fonts"

    fonts = [
        "Bold/complete/DejaVu Sans Mono Bold Nerd Font Complete Mono.ttf",
        "Bold-Italic/complete/DejaVu Sans Mono Bold Oblique Nerd Font Complete Mono.ttf",
        "Italic/complete/DejaVu Sans Mono Oblique Nerd Font Complete Mono.ttf",
        "Regular/complete/DejaVu Sans Mono Nerd Font Complete Mono.ttf",
    ]

    print("Installing fonts...")
    with RunAndDone(font_dir):
        for font in fonts:
            url = f"https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/DejaVuSansMono/{font}"
            filename = font.split("/")[-1]
            res = requests.get(url)
            with open(filename, "wb+") as fd:
                fd.write(res.content)
            
            if os_name == "Linux":
                # On linux, refresh the font cache
                call(f"fc-cache -f ${font_dir}")

    _install_fonts_done = True

_install_latte_dock_done = False

def install_latte_dock():
    """
    Install Latte dock

    Installs the latest version of latte dock from https://github.com/KDE/latte-dock.
    Requires sudo privileges.

    This should only be run on Ubuntu (installation steps differ with other
    distros) with KDE installed
    """

    global _install_fonts_done

    if _install_fonts_done:
        return

    # Install dependencies needed to build
    deps = [
        'build-essential',
        'cmake',
        'extra-cmake-modules',
        'gettext',
        'kirigami2-dev',
        'libkf5activities-dev',
        'libkf5archive-dev',
        'libkf5crash-dev',
        'libkf5declarative-dev',
        'libkf5iconthemes-dev',
        'libkf5newstuff-dev',
        'libkf5notifications-dev',
        'libkf5plasma-dev',
        'libkf5wayland-dev',
        'libkf5windowsystem-dev',
        'libkf5xmlgui-dev',
        'libqt5waylandclient5-dev',
        'libqt5x11extras5-dev',
        'libsm-dev',
        'libwayland-client++0',
        'libwayland-dev',
        'libx11-dev',
        'libx11-xcb-dev',
        'libxcb-randr0-dev',
        'libxcb-shape0-dev',
        'libxcb-util-dev',
        'libxcb-util0-dev',
        'plasma-wayland-protocols',
        'qtdeclarative5-dev',
        'qtwayland5-dev-tools'
    ]

    # Root access needed to install dependencies
    sudo()

    # Install dependencies
    call("sudo add-apt-repository ppa:kubuntu-ppa/backports")
    call("sudo apt update")
    call("sudo apt dist-upgrade")
    call("sudo apt install -y " + " ".join(deps))

    print("Installing latte-dock...")

    # Some installers we want to stick around, specifically so we can update and 
    # rebuild when things go awry. The `software` folder is in .gitignore and 
    # should be kept around.
    with RunAndDone(f"{DOTFILES_DIR}/software/latte-dock", purge=True):
        clone("https://github.com/KDE/latte-dock.git")
        with RunAndDone("latte-dock"):
            call("sh install.sh", check=True)

        # If there are issues with the git version, install the stable
        # v9 version from the repositories instead:
        # call("sudo apt install -y latte-dock")

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

def first_install_kubuntu():
    """
    Perform a full first install for Kubuntu

    This installs:
        - A number of CLI utilities (curl, wget, vim, zsh, htop, etc)
        - Snaps for pycharm, slack, and spotify
        - Brave
    """
    # === Install tools and software ===
    APT_TO_INSTALL = [
        "curl",
        "wget",
        "vim",
        "zsh",
        "cmake",
        "build-essential",
        "htop",
        "apt-transport-https",
        "ca-certificates",
        "gnupg-agent",
        "software-properties-common",
    ]

    SNAPS_TO_INSTALL = [
        "slack --classic",
        "pycharm-professional --classic",
        "spotify",
    ]

    sudo()

    call("sudo apt update")

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

    # Install brave
    call("sudo curl -fsSLo "
        "/usr/share/keyrings/brave-browser-archive-keyring.gpg "
        "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg"
    )
    call('echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] '
        'https://brave-browser-apt-release.s3.brave.com/ stable main" '
        '| sudo tee /etc/apt/sources.list.d/brave-browser-release.list'
    )
    call("sudo apt update")
    call("sudo apt install -y brave-browser")

    link_configs()
    setup_shell_unix()
    install_fonts()


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
    link_configs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Bootstrap dotfiles and configuration")
    parser.add_argument(
        "--update",
        "-u",
        action="store_true",
        default=False,
        help="Update packages and configurations",
    )
    parser.add_argument(
        "--full",
        help="Perform a full install. Requires --os."
    )
    parser.add_argument(
        "--os",
        choices=["linux"],
        help="Operating system. Required for full install."
    )
    parser.add_argument(
        "--shell",
        action="store_true",
        default=False,
        help="Set up a shell environment"
    )
    parser.add_argument(
        "--fonts",
        action="store_true",
        default=False,
        help="Install fonts"
    )
    args = parser.parse_args()

    if args.full and not args.os:
        print("Must specify an OS with --os to perform a full install")
        sys.exit(1)

    if args.shell:
        setup_shell_unix()

    if args.fonts:
        install_fonts()

    if args.update:
        update()
    else:
        first_install()
