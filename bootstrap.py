#!/usr/bin/env python3

"""
Setup dotfiles and system configuration.

This script is broken into two sections:
    1. Install necessary tools and software
    2. Load configurations
"""

import argparse
import functools
import os
from pathlib import Path
import platform
from shutil import rmtree
from subprocess import run
import sys
from typing import Union

os_name = platform.system()
arch = platform.machine()

if os_name not in ("Linux", "Darwin"):
    print(f"{os_name} is not a supported environment")
    sys.exit(1)

if arch not in ("x86_64", "arm64"):
    print(f"{arch} is not a supported architecture")
    sys.exit(1)


# Make sure we're working from the right place
DOTFILES_DIR = Path(__file__).resolve().parent
os.chdir(DOTFILES_DIR)

# getlogin() has caveats, but for running an install script it should suffice
USER = os.getlogin()
HOME = os.environ["HOME"]

# For each supported OS, map destination locations
# to dotfiles that should be linked there
DOTFILE_LOCATIONS: dict[str, dict[str, list[str]]] = {
    "Linux": {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".p10k.zsh", ".gitconfig"],
        f"{HOME}/.local/share/konsole": ["konsole.profile"],
        f"{HOME}/.config": ["kwinrc"],
        # f"{HOME}/.config/latte": ["Condensed.layout.latte"], # Must be imported manually
    },
    "Darwin": {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".p10k.zsh", ".gitconfig"],
    },
}


def once(func):
    """
    Decorator to make sure a function only gets called once
    """
    ran = False

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal ran
        if ran:
            return

        res = func(*args, **kwargs)
        ran = True

        return res

    return wrapper


@once
def sudo():
    call("sudo -v")


def call(args, check=False, env=None):
    return run(args.strip().split(" "), check=check, env=env)


def clone(repo, destination="", args=""):
    if os.path.isdir(destination):
        raise FileExistsError(
            f"{destination} already exists. Did you mean to run with --update?"
        )

    call(f"git clone {repo} {destination} {args}")


def prompt_bool(prompt: str) -> bool:
    """
    Prompt the user for a boolean (y/n) input
    """
    prompt += " [y/n] "
    while True:
        result = input(prompt).lower()
        if result.startswith("y"):
            return True
        elif result.startswith("n"):
            return False


class RunAndDone:
    """
    chdir into the specified directory, and return to the previous directory on exit
    """

    def __init__(self, path: Union[str, Path], create=True, purge=False):
        """
        :param path: Path to chdir into
        :param create: If True, create the directory before entering
        :param purge: If True, then the directory will be removed then re-created
        """
        if not isinstance(path, Path):
            path = Path(path)
        self.path = path
        self.create = create
        self.purge = purge

    def __enter__(self):
        self.prev_path = os.getcwd()
        if self.purge and self.path.is_dir():
            rmtree(self.path)

        if self.create and not self.path.is_dir():
            self.path.mkdir(parents=True)

        os.chdir(self.path)

    def __exit__(self, *args):
        os.chdir(self.prev_path)


@once
def link_configs():
    configs = DOTFILE_LOCATIONS[os_name]

    for path, dotfiles in configs.items():
        with RunAndDone(path):
            for dotfile in dotfiles:
                df = Path(dotfile)
                if df.exists():
                    prompt = f"{dotfile} already exists"
                    if df.is_symlink():
                        prompt += f" ({df.absolute()} -> {df.resolve()})"
                    prompt += ". Overwrite?"

                    overwrite = prompt_bool(prompt)

                    if overwrite:
                        # Delete the existing file
                        df.unlink()
                    else:
                        continue

                source = DOTFILES_DIR / dotfile
                df.symlink_to(source)


@once
def setup_shell_unix():
    """
    Sets up my preferred shell with Oh My Zsh, Powerlevel10k,
    and miniconda on any Mac or Linux machine.

    This assumes that zsh is already installed.

    Does not require privileged execution, so this can be executed
    anywhere.
    """

    # Install the latest version of Oh My Zsh the recommended way.
    # This also sets the default shell to zsh if possible (if not,
    # you may need to set it manually).
    print("Installing Oh My Zsh...")
    call(
        "curl -Lo oh-my-zsh_install.sh https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
    )
    call("sh oh-my-zsh_install.sh", env={**os.environ, "CHSH": "yes", "RUNZSH": "no"})
    os.remove("oh-my-zsh_install.sh")

    # Install Powerlevel10k
    print("Installing powerlevel10k...")
    clone(
        "https://github.com/romkatv/powerlevel10k.git",
        f"{HOME}/.oh-my-zsh/custom/themes/powerlevel10k",
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
    if os.path.isdir(f"{HOME}/.miniconda3"):
        print(f"{HOME}/.miniconda3/ already exists. Skipping install")
    else:
        if os_name == "Linux":
            miniconda_installer = (
                "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
            )
        elif os_name == "Darwin" and arch == "x86_64":
            miniconda_installer = (
                "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            )
        elif os_name == "Darwin" and arch == "arm64":
            miniconda_installer = (
                "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
            )

        call(f"curl -Lo miniconda3_install.sh {miniconda_installer}")
        call(f"sh miniconda3_install.sh -b -p ${HOME}/.miniconda3")
        os.remove("miniconda3_install.sh")

    # Install Rust and Cargo
    call("curl https://sh.rustup.rs -sSf | sh")


@once
def update_shell_unix():
    """
    Updates shell components set up by `setup_shell_unix
    """

    # Re-link configs
    link_configs()

    # Update Oh My Zsh
    print("Updating oh-my-zsh...")
    with RunAndDone(f"{HOME}/.oh-my-zsh/", create=False):
        call("sh upgrade.sh")

    # Update powerlevel10k
    print("Updating powerlevel10k...")
    with RunAndDone(f"{HOME}/.oh-my-zsh/custom/themes/powerlevel10k/"):
        call("git pull origin master")

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


@once
def install_fonts():
    """
    Installs terminal fonts on Mac on Linux.

    This does not need to be run on remote machines, only clients.

    Fonts to install:
        - DejaVu Sans Mono
    """

    if os_name == "Linux":
        font_dir = f"{HOME}/.local/share/fonts"
    elif os_name == "Darwin":
        font_dir = f"{HOME}/Library/Fonts"
    else:
        raise ValueError(f"Unsupported OS: {os_name}")

    download_url = (
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/{name}.zip"
    )

    fonts = ["DejaVuSansMono"]

    # Extra files in the zip archive that can be removed
    extra_files_to_remove = ["README.md", "LICENSE.txt"]

    print("Installing fonts...")
    with RunAndDone(font_dir):
        for font in fonts:
            url = download_url.format(name=font)
            filename = f"{font}.zip"

            call(f"curl -Lo {filename} {url}")
            call(f"unzip {filename}")
            os.remove(filename)

            # Remove files that come along with the font
            for f in extra_files_to_remove:
                if os.path.isfile(f):
                    os.remove(f)

            if os_name == "Linux":
                # On linux, refresh the font cache
                call(f"fc-cache -f ${font_dir}")


@once
def install_latte_dock():
    """
    Install Latte dock

    Installs the latest version of latte dock from https://github.com/KDE/latte-dock.
    Requires sudo privileges.

    This should only be run on Ubuntu (installation steps differ with other
    distros) with KDE installed
    """

    # Install dependencies needed to build
    deps = [
        "build-essential",
        "cmake",
        "extra-cmake-modules",
        "gettext",
        "kirigami2-dev",
        "libkf5activities-dev",
        "libkf5archive-dev",
        "libkf5crash-dev",
        "libkf5declarative-dev",
        "libkf5iconthemes-dev",
        "libkf5newstuff-dev",
        "libkf5notifications-dev",
        "libkf5plasma-dev",
        "libkf5wayland-dev",
        "libkf5windowsystem-dev",
        "libkf5xmlgui-dev",
        "libqt5waylandclient5-dev",
        "libqt5x11extras5-dev",
        "libsm-dev",
        "libwayland-client++0",
        "libwayland-dev",
        "libx11-dev",
        "libx11-xcb-dev",
        "libxcb-randr0-dev",
        "libxcb-shape0-dev",
        "libxcb-util-dev",
        "libxcb-util0-dev",
        "plasma-wayland-protocols",
        "qtdeclarative5-dev",
        "qtwayland5-dev-tools",
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
    with RunAndDone(DOTFILES_DIR / "software" / "latte-dock", purge=True):
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


@once
def update_latte_dock():
    print("Updating latte-dock...")
    with RunAndDone(DOTFILES_DIR / "software", create=False):
        # Install latte-dock, applets, and other tweaks
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


@once
def first_install_kubuntu(latte_dock=False):
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
    call(
        "sudo curl -fsSLo "
        "/usr/share/keyrings/brave-browser-archive-keyring.gpg "
        "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg"
    )
    call(
        'echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] '
        'https://brave-browser-apt-release.s3.brave.com/ stable main" '
        "| sudo tee /etc/apt/sources.list.d/brave-browser-release.list"
    )
    call("sudo apt update")
    call("sudo apt install -y brave-browser")

    link_configs()
    setup_shell_unix()
    install_fonts()

    if latte_dock:
        install_latte_dock()


@once
def update_ubuntu(latte_dock=False):
    """
    Update tools and software for Ubuntu
    """

    sudo()

    # Re-link configs
    link_configs()

    # Update shell
    update_shell_unix()

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

    if latte_dock:
        update_latte_dock()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Bootstrap dotfiles and configuration")
    parser.add_argument(
        "--update",
        "-u",
        action="store_true",
        default=False,
        help="Updates configs and shell. To update packages, pass --full",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Perform a full install. Includes shell and fonts.",
    )
    parser.add_argument(
        "--shell", action="store_true", default=False, help="Set up a shell environment"
    )
    parser.add_argument(
        "--fonts", action="store_true", default=False, help="Install fonts"
    )
    parser.add_argument(
        "--latte-dock",
        action="store_true",
        default=False,
        help="Install latte-dock (KDE only)",
    )
    parser.add_argument(
        "--configs", action="store_true", default=False, help="Link configs"
    )
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if args.shell:
        setup_shell_unix()

    if args.fonts:
        install_fonts()

    if args.configs:
        link_configs()

    if args.full and not args.update:
        # Full install only
        if os_name == "Linux":
            first_install_kubuntu(latte_dock=args.latte_dock)
        else:
            print(f"Full install not supported for {os_name}")
    elif args.update:
        if args.full:
            # Full OS update
            if os_name == "Linux":
                update_ubuntu(latte_dock=args.latte_dock)
            else:
                print(f"Full update not supported for {os_name}")
        else:
            # Just update configs and shell
            link_configs()
            update_shell_unix()

