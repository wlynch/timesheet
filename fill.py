#!/usr/local/bin/python2.7
from datetime import datetime, timedelta, time
import pprint
import yaml
from fdfgen import forge_fdf
from commands import getoutput

pp = pprint.PrettyPrinter(indent=4)


FIRST_NAME = 'William'
LAST_NAME = 'Lynch'
EMPLOYEE_ID = '1234'

# Goes from monday to sunday
WEEK = [
	(),
	(),
	('13:00','16:00'),
	(),
	(),
	(),
	(),
]

def get_start_of_pay_period(date):
	return date - timedelta(days=date.weekday(), weeks=1)

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

def generate_pdf(fields, name):
	fdf = forge_fdf('', fields.items(), [], [], [])

	with open('data.fdf', 'w') as fdf_file:
		fdf_file.write(fdf)

	return getoutput('pdftk timesheet.pdf fill_form data.fdf output %s.pdf flatten' % (name))

def set_fields(start_date, end_date, first_name, last_name, employee_id, payrate, week):
	curr_date = end_date
	while(curr_date >= start_date):
		start = get_start_of_pay_period(curr_date)

		curr_date -= timedelta(weeks=2)

		fields = {
			'First Name': FIRST_NAME,
			'Last Name': LAST_NAME,
						'SS': EMPLOYEE_ID,
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
		for week in range(1, 3):
			total_hours = 0
			for i in range(0, 7):
				if week == 1:
					num = str(i + 1)
				else:
					num = str(7 + i + 1)

				
				if WEEK[i]:
					start_time = parse_time(WEEK[i][0])
					end_time = parse_time(WEEK[i][1])

					fields['F' + num] = format_time(start_time)
					fields['T' + num] = format_time(end_time)
					
					total_hours += hours_elapsed(start_time, end_time)

			fields['Week %d Total' % (week)] = str(total_hours)
			fields['Sum%d' % (week)] = str(total_hours)
			if week == 1:
				fields['Hours 1'] = str(total_hours)
			else:
				fields['Hours 4'] = str(total_hours)

			all_hours += total_hours

		fields['Comments'] = 'Peer Leader work with Andrew Tjang \n%.02f/hrs X $12/hr = $%.02f' % (all_hours, all_hours * 12.0)

	return fields

def parse_yaml(config_file):
	stream = open("example.yaml", 'r')
	return yaml.load(stream)

def get_work_week(config):
	weekdays = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
	week = [(), (), (), (), (), (), ()]
	for event in config['schedule']:
		week[weekdays[event['day']]] = (event['start'], event['end'])
	return week

if __name__ == '__main__':
	end_date = datetime(day=12, month=4, year=2013)
	start_date = datetime(day=12, month=4, year=2013)
	config = parse_yaml('example.py')
	
	fields = set_fields(start_date, end_date, config['first_name'], config['last_name'], config['employee_id'], config['payrate'], get_work_week(config))
	#pp.pprint(fields)

	name = end_date.strftime('%m-%d-%y')
	generate_pdf(fields, name)
	print "Generated %s.pdf!" % (name)
