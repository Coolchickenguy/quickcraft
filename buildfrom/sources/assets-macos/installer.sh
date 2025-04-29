#!/bin/sh
# Check for python3
if command -v python3 > /dev/null 2>&1 && command -v pip3 > /dev/null 2>&1; then
    echo "Python 3 and pip3 are installed. Continuing"
else
    # Run the installation function
    echo "Please install python3/pip3"
    exit 1
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