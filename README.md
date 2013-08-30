timesheet
=========

Timesheet generation for CS111

## How to use
1. Generate a .yaml file with your employee configuration settings. The script will look in ~/payroll.yaml by default, but can be specified by the --config flag.
2. Run the script, specifiying the end of the pay period. If no date is given, the current week is used for the last week of the pay period.
3. The timestamped timesheet will be be put in the user's home directory unless specified by the --output flag.

## Dependencies
* PyYAML
* fdfgen
* pdftk
