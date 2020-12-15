# webpage-monitor

A macOS-based webpage monitor that sends you an email of a webpage's before
and after when changes are detected.


## Installing

1. Install `webkit2png` with:
   ```
   brew install webkit2png
   ```

1. Create a conda environment with all dependencies:
   ```
   conda env create -f environment.yml
   ```


## Running

1. Specify the URLs that you'd like to track by editing `roster.json`.

1. Create a file, named `gmail_app_pswd`, with its content being your Gmail
   app-specific password (a Gmail-only password; see how to set one
   up [here](https://support.google.com/accounts/answer/185833?hl=en)).

1. Activate the environment and run the monitor:
   ```
   conda activate webpage-monitor

   # This conda environment's Python binary will be used
   ./run.py
   ```
