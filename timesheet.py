#!/usr/bin/env python
from datetime import datetime, timedelta, time, date
from fdfgen import forge_fdf
from commands import getoutput
import argparse, os, sys, tempfile, yaml

def format_date(date):
	return date.strftime('%m/%d/%y')

def format_time(time):
	return '%s:%.2d' % (time.hour, time.minute)

def parse_time(string):
	hour, minute = string.split(':')
	return time(hour=int(hour), minute=int(minute))

def hours_elapsed(start, end):
	start_dec = start.hour + start.minute / 60.0
	end_dec = end.hour + end.minute / 60.0
	return end_dec - start_dec

def generate_pdf(fields, template, output):
	fdf = forge_fdf('', fields.items(), [], [], [])
	temp = tempfile.NamedTemporaryFile()
	with open(temp.name, 'w') as fdf_file:
		fdf_file.write(fdf)
	getoutput('pdftk %s fill_form %s output %s.pdf flatten' % (template, fdf_file.name, output))
	fdf_file.close()
	temp.close()

def set_fields(start_date, end_date, first_name, last_name, employee_id, payrate, week):
	curr_date = end_date
	while(curr_date >= start_date):
		start = curr_date - timedelta(days=curr_date.weekday(), weeks=1)
		curr_date -= timedelta(weeks=2)

		fields = {
			'First Name': first_name,
			'Last Name': last_name,
			'SS': employee_id,
			'Rate': str(payrate),
		}

		# populate them dates.
		for i in range(0, 14):
			num = str(i + 1)
			fields['D'+ num] = format_date(start + timedelta(days=i))

		friday = start + timedelta(days=4)
		next_friday = friday + timedelta(weeks=1)

		fields['Week Ending 1'] = format_date(friday)
		fields['Week Ending 2'] = format_date(next_friday)

		all_hours = 0

		# populate weeks
		for week_num in range(1, 3):
			total_hours = 0
			for i in range(0, 7):
				if week_num == 1:
					num = str(i + 1)
				else:
					num = str(7 + i + 1)

				if week[i]:
					start_time = parse_time(week[i][0])
					end_time = parse_time(week[i][1])

					fields['F' + num] = format_time(start_time)
					fields['T' + num] = format_time(end_time)
					fields['Day' + num] = str(hours_elapsed(start_time, end_time))
					
					total_hours += hours_elapsed(start_time, end_time)

			fields['Week %d Total' % (week_num)] = str(total_hours)
			fields['Sum%d' % (week_num)] = str(total_hours)
			if week_num == 1:
				fields['Hours 1'] = str(total_hours)
			else:
				fields['Hours 4'] = str(total_hours)

			all_hours += total_hours

		fields['Comments'] = 'Peer Leader work with Andrew Tjang \n%.02f/hrs X $%.02f/hr = $%.02f' % (all_hours, payrate, all_hours * payrate)

	return fields

def parse_yaml(config_file):
	stream = open(config_file, 'r')
	config = yaml.load(stream)
	stream.close()
	return config

def get_work_week(config):
	weekdays = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
	week = [(), (), (), (), (), (), ()]
	if config and 'schedule' in config:
		for event in config['schedule']:
			week[weekdays[event['day']]] = (event['start'], event['end'])
	return week

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate timesheets for CS111 payroll')
	parser.add_argument("date", type=str, nargs='?', help="end of pay period")
	parser.add_argument("--config", default=os.getenv("HOME") + '/payroll.yaml', help="employee config file")
	parser.add_argument("--template", default=os.path.dirname(os.path.realpath(__file__)) + '/timesheet.pdf', help="pdf template file")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--output", help="output file")
	group.add_argument("--output_dir", help="output directory")
	args = parser.parse_args()
	
	if args.date: 
		due = args.date.rsplit('/')
		end_date = datetime(day=int(due[1]), month=int(due[0]), year=int(due[2]))
	else:
		end_date = date.today()
		end_date = end_date + timedelta(days=4-end_date.weekday())
	start_date = end_date - timedelta(days=4, weeks=1)
	
	config = parse_yaml(args.config)
	week = get_work_week(config)
	if config:
		fields = set_fields(start_date, end_date, config.get('first_name', ''), config.get('last_name', ''), config.get('employee_id', ''), config.get('payrate', 0), week)
		prefix = config.get('last_name', 'timesheet')
	else:
		fields = set_fields(start_date, end_date, '', '', '', 0, week)
		prefix = 'timesheet'

	if args.output:
		output = args.output
	elif args.output_dir:
		output = args.output_dir + '/' + prefix + '-' + end_date.strftime('%m-%d-%y')
	else:
		output = os.getenv("HOME") + '/' + prefix + '-' + end_date.strftime('%m-%d-%y')
	generate_pdf(fields, args.template, output)
	print "Generated %s.pdf!" % (output)
