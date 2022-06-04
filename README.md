# webpage-monitor

A minimal webpage monitor that continuously compares a site's HTML against its
past snapshot and sends you an email of the deltas if any.

I'm using it to monitor website updates of the researchers I follow (e.g., new papers).

![teaser](https://xiuming.info/images/side_proj/webpage_monitor.jpg)

## Installing

Create a conda environment with all dependencies:

 ```bash
 conda env create -f environment.yml
 ```

## Running

1. Specify the URLs that you'd like to track (and optional URL-specific
arguments) by editing `./roster.json`.

1. Create a file `./gmail_app_pswd`, with its content being your Gmail
*app-specific* password (NOT your Google account password; see how to set one
up [here](https://support.google.com/accounts/answer/185833?hl=en)).

1. Activate the environment and run the monitor:

```bash
conda activate webpage-monitor
python main.py
```
