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
import platform
import shlex
import sys
import tempfile
from pathlib import Path
from shutil import rmtree, which
from subprocess import run
from typing import Union
from urllib.request import urlretrieve

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

HOME = os.environ["HOME"]

# For each supported OS, map destination locations
# to dotfiles that should be linked there
DOTFILE_LOCATIONS: dict[str, dict[str, list[str]]] = {
    "Linux": {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".p10k.zsh", ".gitconfig"],
        f"{HOME}/.local/share/konsole": ["konsole.profile"],
    },
    "Darwin": {
        HOME: [".vimrc", ".tmux.conf", ".zshrc", ".p10k.zsh", ".gitconfig"],
    },
}

# Paths
ZSH_SYNTAX_HIGHLIGHTING_PATH = (
    f"{HOME}/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting"
)
ZSH_AUTOSUGGESTIONS_PATH = f"{HOME}/.oh-my-zsh/custom/plugins/zsh-autosuggestions"
POWERLEVEL10K_PATH = f"{HOME}/.oh-my-zsh/custom/themes/powerlevel10k/"


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


def call(args, check=True, env=None):
    return run(shlex.split(args), check=check, env=env)


def clone(repo, destination="", args=""):
    if os.path.isdir(destination):
        raise FileExistsError(
            f"{destination} already exists. Did you mean to run with --update?"
        )

    call(f"git clone {repo} {destination} {args}")


def install_script(url, args="", shell="sh", env=None):
    """
    Download a shell installer from `url`, run it (passing any `args`),
    and remove the downloaded file afterwards.

    :param url: URL to download
    :param args: Arguments to pass to the script
    :param shell: Shell to use, default sh
    :param env: Extra environment variables to pass to the script
    """
    fd, script = tempfile.mkstemp(suffix=".sh")
    os.close(fd)
    try:
        urlretrieve(url, script)
        call(f"{shell} {script} {args}", env={**os.environ, **(env or {})})
    finally:
        os.remove(script)


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


class Pushd:
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
        with Pushd(path):
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
    if os.path.isdir(f"{HOME}/.oh-my-zsh/"):
        print("Oh My Zsh already installed. Skipping.")
    else:
        install_script(
            "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh",
            env={"CHSH": "yes", "RUNZSH": "no"},
        )

    # Install Powerlevel10k
    print("Installing powerlevel10k...")
    if os.path.isdir(POWERLEVEL10K_PATH):
        print("powerlevel10k already installed. Skipping.")
    else:
        clone(
            "https://github.com/romkatv/powerlevel10k.git",
            POWERLEVEL10K_PATH,
        )

    # Install zsh plugins
    print("Installing oh-my-zsh plugins...")
    if os.path.isdir(ZSH_SYNTAX_HIGHLIGHTING_PATH):
        print("zsh-syntax-highlighting already installed. Skipping.")
    else:
        clone(
            "https://github.com/zsh-users/zsh-syntax-highlighting.git",
            ZSH_SYNTAX_HIGHLIGHTING_PATH,
        )

    if os.path.isdir(ZSH_AUTOSUGGESTIONS_PATH):
        print("zsh-autosuggestions already installed. Skipping.")
    else:
        clone(
            "https://github.com/zsh-users/zsh-autosuggestions",
            ZSH_AUTOSUGGESTIONS_PATH,
        )

    # Install Miniconda 3
    #
    # Running the installer with -b will install in silent mode,
    # and not initialize the shell. The .zshrc file in this repo
    # already has the `conda init zsh` output in it.
    print("Installing Miniconda")
    if os.path.isdir(f"{HOME}/.miniconda3"):
        print("Miniconda already installed. Skipping.")
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
        else:
            raise RuntimeError(f"No Miniconda installer for {os_name}/{arch}")

        install_script(miniconda_installer, f"-b -p {HOME}/.miniconda3")

    # Install uv
    print("Installing uv")
    if which("uv") is not None:
        print("uv already installed. Skipping.")
    else:
        install_script("https://astral.sh/uv/install.sh")

    # Install Rust and Cargo
    print("Installing Rust")
    if which("rustup") is not None:
        print("Rust already installed. Skipping.")
    else:
        install_script("https://sh.rustup.rs", "--no-modify-path -y")


@once
def update_shell_unix():
    """
    Updates shell components set up by `setup_shell_unix`
    """

    # Re-link configs
    link_configs()

    # Update Oh My Zsh
    print("Updating oh-my-zsh...")
    with Pushd(f"{HOME}/.oh-my-zsh/", create=False):
        call("sh tools/upgrade.sh")

    # Update powerlevel10k
    print("Updating powerlevel10k...")
    with Pushd(POWERLEVEL10K_PATH, create=False):
        call("git pull origin master")

    # Update zsh plugins
    print("Updating oh-my-zsh plugins...")
    with Pushd(ZSH_SYNTAX_HIGHLIGHTING_PATH, create=False):
        call("git pull origin master")

    with Pushd(ZSH_AUTOSUGGESTIONS_PATH, create=False):
        call("git pull origin master")

    # Update uv
    print("Updating uv...")
    call("uv self update")

    # Update Rust
    print("Updating rust...")
    call("rustup update")


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
    with Pushd(font_dir):
        for font in fonts:
            url = download_url.format(name=font)
            filename = f"{font}.zip"

            urlretrieve(url, filename)
            call(f"unzip {filename}")
            os.remove(filename)

            # Remove files that come along with the font
            for f in extra_files_to_remove:
                if os.path.isfile(f):
                    os.remove(f)

            if os_name == "Linux":
                # On linux, refresh the font cache
                call(f"fc-cache -f {font_dir}")


def link_snap_desktop_entries():
    """
    Symlink snap desktop entries

    This is necessary because krunner can't find them for some reason.
    """
    snap_apps = "/var/lib/snapd/desktop/applications"
    with Pushd(f"{HOME}/.local/share/applications"):
        for file in os.listdir(snap_apps):
            if not file.endswith(".desktop"):
                continue
            call(f"ln -sf {snap_apps}/{file} .")


@once
def first_install_kubuntu():
    """
    Perform a full first install for Kubuntu

    This installs:
        - A number of CLI utilities (curl, wget, vim, zsh, htop, etc)
        - Snaps for slack and spotify
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

    link_snap_desktop_entries()

    # Install brave
    call(
        "sudo curl -fsSLo "
        "/usr/share/keyrings/brave-browser-archive-keyring.gpg "
        "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg"
    )
    call(
        "sudo curl -fsSLo "
        "/etc/apt/sources.list.d/brave-browser-release.sources "
        "https://brave-browser-apt-release.s3.brave.com/brave-browser.sources"
    )
    call("sudo apt update")
    call("sudo apt install -y brave-browser")

    link_configs()
    setup_shell_unix()
    install_fonts()


@once
def update_ubuntu():
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
    call("sudo snap refresh")

    link_snap_desktop_entries()


@once
def first_install_mac():
    """
    Perform a full first install for Mac

    This installs:
        - Homebrew
    """

    sudo()

    # Install homebrew
    install_script(
        "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh",
        shell="bash",
        env={"NONINTERACTIVE": "1"},
    )

    brew_to_install = [
        "htop",
        # Kubernetes things
        "kubectl",
        "derailed/k9s/k9s",
        "fluxcd/tap/flux",
    ]

    for formula in brew_to_install:
        call(f"brew install -y {formula}")

    link_configs()
    setup_shell_unix()
    install_fonts()


@once
def update_mac():
    """
    Update tools and software for Mac
    """

    sudo()

    # Re-link configs
    link_configs()

    # Update shell
    update_shell_unix()

    # Update homebrew formulae
    call("brew update")
    call("brew upgrade")


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
            first_install_kubuntu()
        elif os_name == "Darwin":
            first_install_mac()
        else:
            print(f"Full install not supported for {os_name}")
    elif args.update:
        if args.full:
            # Full OS update
            if os_name == "Linux":
                update_ubuntu()
            elif os_name == "Darwin":
                update_mac()
            else:
                print(f"Full update not supported for {os_name}")
        else:
            # Just update configs and shell
            link_configs()
            update_shell_unix()
