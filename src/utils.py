import sys
import json

# Splits data by UTC time (number of seconds that have elapsed since January 1, 1970) - in GMT, not local time
#   1 hour = 3600 seconds
#   1 day  = 86400 seconds
#   1 week = 604800 seconds
# Examples:
#   October 26, 2016, 00:00:00:  1477440000
#   November 23, 2016, 23:59:59: 1479945599
def split_data_by_time(input_file, output_file, start, end):
    file = open(input_file, 'r')
    filtered_file = open(output_file, 'w')

    total_obj = 0
    written_obj = 0

    while True:
        line = file.readline()

        if len(line) == 0:
            break

        total_obj += 1

        data = json.loads(line)

        created_on = data['created_utc']
        if created_on < start or created_on > end:
            continue

        json.dump(data, filtered_file)
        filtered_file.write('\n')
        written_obj += 1

    print('Total objects: {}'.format(total_obj))
    print('Written objects: {}'.format(written_obj))
    filtered_file.close()


def split_data_by_sentiment_range(input_file, output_file, type, low=-1, high=1):
    """ Types include: neg, neu, pos, compound"""

    file = open(input_file, 'r')
    filtered_file = open(output_file, 'w')

    total_obj = 0
    written_obj = 0

    while True:
        line = file.readline()

        if len(line) == 0:
            break

        total_obj += 1

        data = json.loads(line)

        sentiment = data['sentiment']

        if sentiment[type] < low or sentiment[type] > high:
            continue

        json.dump(data, filtered_file)
        filtered_file.write('\n')
        written_obj += 1

    print('Total objects: {}'.format(total_obj))
    print('Written objects: {}'.format(written_obj))
    filtered_file.close()


def print_data(input_file, num_lines):
    file = open(input_file, 'r')
    total_obj = 0

    while total_obj < num_lines:
        line = file.readline()

        if len(line) == 0:
            break

        total_obj += 1
        print(json.loads(line))

