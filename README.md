# webpage-monitor

A minimal webpage monitor that continuously compares a site's HTML against its
past snapshot and sends you an email of the deltas if any.

I'm using it to monitor website updates of the researchers I follow (e.g., new papers).

![teaser](teaser.jpg)

## Installing

Create a conda environment with all dependencies:

 ```bash
 conda env create -f environment.yml
 ```

## Running

1. Specify the URLs that you'd like to track (and optionally, their options) by
editing `roster.json`; see `roster.json.example`.

1. Edit `gmail_app_pswd`, with its content being your Gmail app-specific password
(a Gmail-only password; see how to set one up [here](https://support.google.com/accounts/answer/185833?hl=en)).

1. Activate the environment and run the monitor:

```bash
conda activate webpage-monitor
python main.py
```
