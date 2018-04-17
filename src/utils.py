import sys, json, string, re, csv, operator
from collections import Counter
import pprint

# Splits data by UTC time (number of seconds that have elapsed since January 1, 1970) - in GMT, not local time
#   1 hour = 3600 seconds
#   1 day  = 86400 seconds
#   1 week = 604800 seconds
# 
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


def load_stopwords():
    results = []
    with open("../Data/stopwords.csv") as csvfile:
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
    print("Starting to extract text from comments")
    file = open(input_file, 'r')

    total_obj = 0
    written_obj = 0

    if filter:
        stop_words_arr = load_stopwords()

        punctuation_translator = str.maketrans(' ', ' ', string.punctuation)
        num_regex = re.compile(r'[0-9]+')
        whitespace_chars_regex = re.compile(r'[\n\r\t]+')

    text_arr = []
    while True:
        line = file.readline()

        if len(line) == 0:
            break

        total_obj += 1
        
        body = json.loads(line)['body']

        if filter:
            body = body.lower()
            # Remove all numbers from comments
            body = num_regex.sub("", body)

            # Remove all punctuation from comments
            body = body.translate(punctuation_translator)

            # Remove all special whitespace characters
            body = whitespace_chars_regex.sub(" ", body)

        text_arr.append(body)

    output.close()

    if filter:
        pre_stop_removal = len(text_arr)
        text_arr = [el for el in text_arr if el not in stop_words_arr and len(el) > 0]
        post_stop_removal = len(text_arr)

        print("Removed {} words by removing stop words. Ending with {} words.".format(pre_stop_removal-post_stop_removal, post_stop_removal))

    return text_arr


def get_top_n_words_from_text(text_arr, n):
    '''
        text_arr is an array of strings that will be converted to 
        a dictionary sorted by the integer value representing
        how many times each unique string appears in the array.

        Returns top n occuring strings as an array of tuples in
        the form (string, num_occurrences).
    '''
    keys = Counter(text_arr).keys()
    values = Counter(text_arr).values()
    dictionary = dict(zip(keys, values))
    print("Found {} unique words.".format(len(dictionary)))

    sorted_words_arr = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_words_arr[:n]


def map_sentiment_to_word(x):
    return {
        'pos': 'positive',
        'neu': 'neutral',
        'neg': 'negative'
    }[x]
