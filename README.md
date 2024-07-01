# data-annotation-alerts

set up this script with mac crontab to get automated alerts on new DataAnnotation projects. developed with ChatGPT 4.0.

## steps

1. clone repo
2. populate `gmail`, `gmail_password`, `data_annotation_email`, `data_annotation_password` and `fpath` fields
3. in Mac Terminal, type `crontab -e` to add a cron job
4. type `i` to enter editing mode
5. add a line in the form of `* * * * * python3 full/path/to/job_board_alerts.py`, using a cron expression to specify how often the script runs (see https://crontab.guru/ for more info on cron schedule expressions)
6. hit `esc` to exit editing mode, then type `:wq` and hit `enter` to save and exit the crontab editor
