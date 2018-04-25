import sys, json, string, re, csv, operator
import pprint, datetime

from collections import Counter
import pprint
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import SnowballStemmer
import nltk

lmt = WordNetLemmatizer()


class NRCReader:
    def __init__(self, NRCAddress="../Data/NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt"):
        self.nrc_address = NRCAddress
        self.data = {}

    def load(self):
        with open(self.nrc_address, "r", encoding="utf-8") as nrc_file:
            for line in nrc_file.readlines():
                splited = line.replace("\n", "").split("\t")
                word, emotion, value = splited[0], splited[1], splited[2]
                if word in self.data.keys():
                    self.data[word].append((emotion, int(value)))
                else:
                    self.data[word] = [(emotion, int(value))]

    def vectorize(self, sentence:list):
        out = {}
        for word in sentence:
            if word in self.data.keys():
                for item in self.data[word]:
                    if word in out.keys():
                        out[word] += (item[0], item[1])
                    else:
                        out[word] = (item[0], item[1])
        return out

    def get_emotion(self, word, emotion):
        emotions = self.data[word]
        for emot in emotions:
            if emot[0] == emotion:
                return emot[1]

    def get_emotions(self, word):
        emotions = self.data[word]
        return emotions


# Splits data by UTC time (number of seconds that have elapsed since January 1, 1970) - in GMT, not local time
#   1 hour = 3600 seconds
#   1 day  = 86400 seconds
#   1 week = 604800 seconds
#
# Examples:
#   October 26, 2016, 00:00:00:  1477440000
#   November 23, 2016, 23:59:59: 1479945599
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


def read_csv(input_file, header=True, append_data=True):
    results = []
    with open(input_file) as csvfile:
        reader = csv.reader(csvfile)

        if header is False:
            next(reader)

        for row in reader:
            if append_data:
                results.append(row)
            else:
                results.extend(row)
    return results


def extract_text_from_comments(input_file, filter=False, specific_subreddit=None):
    ''' 
        Take an input file of json comment objects and parse
        out all of the text.

        Setting filter to True will convert all text to lower case,
        load stop words from stopwords.csv, and do a manual filtering
        to remove stopwords, punctuation, and numbers from text.
        If not, all text will be outputted.

        Returns text of all comments in input_file and returns
        an array.

        TODO: Ensure this still works as expected
    '''
    file = open(input_file, 'r')

    total_obj = 0

    if filter:
        stop_words_arr = read_csv("../Data/stopwords.csv", header=False, append_data=False)

        punctuation_translator = str.maketrans(' ', ' ', string.punctuation)
        url_regex = re.compile(r'\[?\(?https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)\]?\)?')
        num_regex = re.compile(r'[0-9]+')
        whitespace_chars_regex = re.compile(r'[\n\r\t]+')

    text_arr = []
    times_arr = []
    sentiment_arr = []
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

        subreddit = data['subreddit']
        sentiment = data['sentiment']

        match = True
        if specific_subreddit:
            if subreddit != specific_subreddit:
                match = False

        if match:
            if filter:
                body = body.lower()

                # Remove all numbers from comments
                body = url_regex.sub('', body)
                body = num_regex.sub('', body)

                # Remove all punctuation from comments
                body = body.translate(punctuation_translator)

                # Remove all special whitespace characters
                body = whitespace_chars_regex.sub(' ', body)

                body = ' '.join([el for el in body.split(' ') if el not in stop_words_arr and len(el) > 0])

            text_arr.extend(body.split(' '))
            times_arr.append(time)


    return text_arr, times_arr, sentiment_arr


def get_top_n_words_from_text(text_arr, sentiment_arr, n=-1):
    '''
        text_arr is an array of strings that will be converted to
        a dictionary sorted by the integer value representing
        how many times each unique string appears in the array.

        Returns top n occuring strings as an array of tuples in
        the form (string, num_occurrences, times).

        TODO: Ensure this still works as expected
    '''
    keys = list(Counter(text_arr).keys())
    values = list(Counter(text_arr).values())

    print("Found {} unique words.".format(len(dictionary)))

    sorted_words_arr = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    if n < 0:
        return sorted_words_arr[:(len(dictionary))]

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


def match_words_with_emotion(input_file, filter=False):
    text_arr = extract_text_from_comments(input_file, filter)
    print("Lemmatizing sentences...")
    text_arr = list(map(nat_lang_sentence, text_arr))
    print("Lemmatized the sentences")
    all_words = get_top_n_words_from_text(text_arr)
    text_arr = None
    nrc = NRCReader()
    nrc.load()

    words = [el for el in all_words if el[0] in nrc.data.keys()]
    print("{} out of {} words were found within NRC".format(len(words), len(all_words)))

    filtered_file = open("words_with_count_and_emotions.json", 'w')

    # nrc_emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy',
    #                 'negative', 'positive', 'sadness', 'surprise', 'trust']

    # for sentence in text_arr:
    #     vector = nrc.vectorize(sentence)
    #     print(vector)

    print("Finding emotions for words")

    for w in words:
        output_data = {
            'word': w[0],
            'count': w[1],
            'emotions': {
                'anger': nrc.get_emotion(w[0], 'anger'),
                'anticipation': nrc.get_emotion(w[0], 'anticipation'),
                'disgust': nrc.get_emotion(w[0], 'disgust'),
                'fear': nrc.get_emotion(w[0], 'fear'),
                'joy': nrc.get_emotion(w[0], 'joy'),
                'negative': nrc.get_emotion(w[0], 'negative'),
                'positive': nrc.get_emotion(w[0], 'positive'),
                'sadness': nrc.get_emotion(w[0], 'sadness'),
                'surprise': nrc.get_emotion(w[0], 'surprise'),
                'trust': nrc.get_emotion(w[0], 'trust'),
            },
        }

        json.dump(output_data, filtered_file)
        filtered_file.write('\n')

    print("Done")
    filtered_file.close()


def nat_lang_word(word):
    '''Word stemmer; find the root of the word. E.g. 'dogs' becomes 'dog'''
    return lmt.lemmatize(word)


def nat_lang_sentence(sentence):
    '''Word stemmer; find the root of the word. E.g. 'dogs' becomes 'dog'''
    new_words = list(map(nat_lang_word, sentence.split(' ')))
    return ' '.join(new_words)


def grab_n_lines(input_file, n=1000):
    file = open(input_file, 'r')
    new_file = open("data-{}-lines.json".format(n), 'w')

    counter = 0
    while counter < n:
        line = file.readline()

        if len(line) == 0:
            break

        data = json.loads(line)

        json.dump(data, new_file)
        new_file.write('\n')

        counter += 1

    print('Done')
