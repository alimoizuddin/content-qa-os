#!/usr/bin/env bash
# LinkedIn Content Studio. Run ./run.sh to start the app.
# The first time, it sets itself up and asks for your key. After that it just starts.
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Install it from https://www.python.org/downloads/ and run this again."
  exit 1
fi

if [ ! -x venv/bin/python ]; then
  echo "First run: setting up. This takes a few minutes and only happens once."
  python3 -m venv venv
  venv/bin/python -m pip install --quiet --upgrade pip
  venv/bin/python -m pip install --quiet -r requirements.lock
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo
  echo "A settings file called .env has been created."
  echo "Open it, paste your NVIDIA key after NVIDIA_API_KEY=, save it, and run ./run.sh again."
  exit 0
fi

echo "Starting the app at http://127.0.0.1:8501"
echo "Keep this window open while you use the app. Press Ctrl+C to stop it."
exec venv/bin/python -m streamlit run app.py
