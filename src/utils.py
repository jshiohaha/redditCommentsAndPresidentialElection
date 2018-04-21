import sys, json, string, re, csv, operator
import pprint, datetime

from collections import Counter


def split_data_by_time(input_file, output_file, start, end):
    '''
        Splits data by UTC time (number of seconds that have elapsed 
        since January 1, 1970).

        Examples: October 26, 2016, 00:00:00 --> 1477440000
    '''
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
    ''' Types include: neg, neu, pos, compound'''

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


def load_stopwords():
    results = []
    with open('../Data/stopwords.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            results.extend(row)
    return results


def extract_text_from_comments(input_file, filter=False):
    ''' 
        Take an input file of json comment objects and parse
        out all of the text.

        Setting filter to True will convert all text to lower case, 
        load stop words from stopwords.csv, and do a manual filtering
        to remove stopwords, punctuation, and numbers from text.
        If not, all text will be outputted.

        Returns text of all comments in input_file and returns
        an array.
    '''
    file = open(input_file, 'r')

    total_obj = 0
    written_obj = 0

    if filter:
        stop_words_arr = load_stopwords()

        punctuation_translator = str.maketrans(' ', ' ', string.punctuation)
        num_regex = re.compile(r'[0-9]+')
        whitespace_chars_regex = re.compile(r'[\n\r\t]+')

    text_arr = []
    times_arr = []
    while True:
        line = file.readline()

        if len(line) == 0:
            break

        total_obj += 1

        if total_obj % 100000 == 0:
            print('read {} objects.'.format(total_obj))

        data = json.loads(line)

        body = data['body']
        time = data['created_utc']

        if filter:
            body = body.lower()
            # Remove all numbers from comments
            body = num_regex.sub('', body)

            # Remove all punctuation from comments
            body = body.translate(punctuation_translator)

            # Remove all special whitespace characters
            body = whitespace_chars_regex.sub(' ', body)

            body = ' '.join([el for el in body.split(' ') if el not in stop_words_arr and len(el) > 0])

        text_arr.append(body)
        times_arr.append(time)
    return text_arr, times_arr


def get_top_n_words_from_text(text_arr, n):
    '''
        text_arr is an array of strings that will be converted to 
        a dictionary sorted by the integer value representing
        how many times each unique string appears in the array.

        Returns top n occuring strings as an array of tuples in
        the form (string, num_occurrences, times).
    '''
    times = times_arr if times_arr is not None else None

    keys = Counter(text_arr).keys()
    values = Counter(text_arr).values()

    dictionary = dict(zip(keys, values))
    print('Found {} unique words.'.format(len(dictionary)))

    sorted_words_arr = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_words_arr[:n]


def aggregate_comments_by_day(text_arr, times, group_by='days', group_by_const=1):
    '''
        text_arr is an array of comments and times is an array of times
        corresponding to a 1:1 relationship between comment and time.

        group_by represents the type of bin to group the comments. The options
        are minutes, hours, days, weeks

        Returns an array of tuples in the format of (date string, list of comments).
    '''
    def group_const(group_by, group_by_const):
        return {
            'minutes': (datetime.timedelta(minutes=group_by_const), '%d/%b/%Y, %H:%M'),
            'hours': (datetime.timedelta(hours=group_by_const), '%d/%b/%Y, Hour %H'),
            'days': (datetime.timedelta(days=group_by_const), '%d/%b/%Y'),
            'weeks': (datetime.timedelta(weeks=group_by_const), '%d/%b/%Y'),
        }[group_by]

    timedelta_constant, date_str_format = group_const(group_by, group_by_const)

    # Change this range based on what you are looking for
    start = datetime.datetime.strptime('26/10/16 00:00', '%d/%m/%y %H:%M')
    end = datetime.datetime.strptime('23/11/16 00:00', '%d/%m/%y %H:%M')

    comments_and_dates_by_day = list()

    counter = 0
    while start < end and counter < len(times):
        # add a single day to the datetime object
        temp_dates_arr = list()
        temp_comments_arr = list()

        next_start = start + timedelta_constant
        current_time = datetime.datetime.utcfromtimestamp(times[counter])

        while current_time <= next_start:
            temp_dates_arr.append(current_time)
            temp_comments_arr.append(text_arr[counter])

            counter += 1

            if counter < len(times):
                current_time = datetime.datetime.utcfromtimestamp(times[counter])
            else:
                break

        if len(temp_dates_arr) > 0 and len(temp_comments_arr) > 0:
            time = datetime.datetime.strftime(temp_dates_arr[0], date_str_format)
            comments_and_dates_by_day.append((time, temp_comments_arr))

        start = next_start

    return comments_and_dates_by_day


def map_sentiment_to_word(x):
    return {
        'pos': 'positive',
        'neu': 'neutral',
        'neg': 'negative'
    }[x]
