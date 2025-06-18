#!/bin/sh
rm -rf temp
rm -rf python

#Get me some python

# Function to install Python 3 and pip3
install_python3() {
    echo "Installing Python 3 and pip3..."
    
    # Detect the package manager and install Python 3 and pip3
    if command -v apt-get > /dev/null 2>&1; then
        # For Debian-based distributions (Ubuntu, Debian, etc.)
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3.10-venv
        
    elif command -v dnf > /dev/null 2>&1; then
        # For Red Hat-based distributions (Fedora, CentOS, RHEL)
        sudo dnf install -y python3 python3-pip
        
    elif command -v yum > /dev/null 2>&1; then
        # For older Red Hat-based distributions (CentOS 7, RHEL 7)
        sudo yum install -y python3 python3-pip
        
    elif command -v zypper > /dev/null 2>&1; then
        # For openSUSE
        sudo zypper install -y python3 python3-pip
        
    elif command -v pacman > /dev/null 2>&1; then
        # For Arch Linux and Arch-based distributions
        sudo pacman -Syu --noconfirm python python-pip
        
    elif command -v apk > /dev/null 2>&1; then
        # For Alpine Linux
        sudo apk add python3 py3-pip
        
    else
        echo "Unsupported package manager or distribution."
        exit 1
    fi
}

# Check if Python 3 and pip3 are already installed
if command -v python3 > /dev/null 2>&1 && command -v pip3 > /dev/null 2>&1; then
    echo "Python 3 and pip3 are already installed."
else
    # Run the installation function
    install_python3
fi

# Make venv
python3 -m venv .venv

if command -v source > /dev/null 2>&1; then
  source ./.venv/bin/activate
else
  . ./.venv/bin/activate
fi

# Done installing python
pip3 install -r requirements.txt

# Add desktop shortcut
iconLocation=$(realpath ./logo.png)
localpath=$(realpath ./)
printf "\nIcon=$(realpath ./logo.png)" | tee -a "shortcut.desktop.from"
printf "\nExec=/bin/sh $(realpath ./start.sh)" | tee -a "shortcut.desktop.from"
printf "\nPath=$localpath" | tee -a "shortcut.desktop.from"
cp shortcut.desktop.from ~/.local/share/applications/quickcraft.desktop