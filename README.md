timesheet
=========

Timesheet generation for CS111.

## How to use
1. Generate a .yaml file with your employee configuration settings. The script will look in ~/payroll.yaml by default, 
but can be specified by the --config flag.
2. Run the script, specifiying the end of the pay period. If no date is given, the current week is used for the 
last week of the pay period.
3. The timestamped timesheet will be be put in the user's home directory unless specified by the --output flag.

## Configuration
This script takes in 2 things to generate a timesheet:

1. A template pdf. In most cases the script will know where to look for the template, but you can also specify this 
with the --template flag.
2. A yaml config file.

The yaml config file should be placed at ~/payroll.yaml, but you can specify where this file is with the --config flag.
I am not sure how sensitive some of the data in this file is, so you should probably `chmod 600 payroll.yaml` just in case.
An example config file is:

```
first_name: "Billy"
last_name: "Lynch"
employee_id: "1234"
payrate: 10.00
schedule:
 - day: "friday"
   start: "13:00"
   end: "16:00"
```
Don't know/don't want to put all of this information in the config file? No worries. 
The script should leave them as whatever the default template value was.

#### WARNING: The script does NOT currently support multiple time slots on the same day.

I may or may not get around to fixing this in the near future. Easy solution: Put block times for your hours each week. 
The common practice is to put a 3 (4 if you have 2 recitations) hour block around when you have one of your recitations.
Times do not have to be exact.

## How to run
### iLab
If you have access to the [iLab machines](http://ilab.rutgers.edu), I have already installed the script in my 
home directory for everyone to use.

#### Example usage
```
bash$ ~wlynch92/bin/timesheet
Generated /ilab/users/wlynch92/Lynch-09-13-13.pdf!
```

### Everywhere else
Just clone this repo. It is a simple python script that should be simple to run once you have installed
the dependencies (see below). I have tested this with python 2.6 and 2.7.


## Dependencies
* PyYAML
* fdfgen
* pdftk

## Issues & Feedback
If you encounter a problem or have any feedback, feel free to make a new issue or send me an email.
