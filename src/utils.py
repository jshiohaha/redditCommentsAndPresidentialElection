import sys, json, string, re, csv, operator, html, time
import pprint, datetime
import numpy as np
from collections import Counter
import pprint
from random import randint
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import nltk as nltk

lmt = WordNetLemmatizer()

class NRCReader:
	'''
	    This class converts the given text file into a data object
	    representing the NRC Emotion Lexicon for use in emotion analysis
	'''
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
	'''
	    Prints the first num_lines of a given input_file
	'''
    file = open(input_file, 'r')
    total_obj = 0

    while total_obj < num_lines:
        line = file.readline()

        if len(line) == 0:
            break

        total_obj += 1
        print(json.loads(line))


def read_csv(input_file, header=True, append_data=True):
    '''
        Used to read in "../Data/stopwords.csv" for stop word
        removal in filtering/cleaning comments
    '''
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
    '''
    print("Extracting text from comments...")
    file = open(input_file, 'r')

    total_obj = 0

    if filter:
        stop_words_arr = read_csv("../Data/stopwords.csv")[0]
        stop_words_arr.append('source')

        punctuation_translator = str.maketrans(' ', ' ', string.punctuation)
        url_regex = re.compile(r'\[?\(?https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)\]?\)?')
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

        subreddit = data['subreddit']
        sentiment = data['sentiment']

        match = True
        if specific_subreddit:
            if subreddit != specific_subreddit:
                match = False

        if match:
            if filter:
                body = body.lower()

                # Remove all URLs from comments
                body = url_regex.sub('', body)

                # Remove all numbers from comments
                body = num_regex.sub('', body)

                # Remove all punctuation from comments
                body = body.translate(punctuation_translator)

                # Remove all special whitespace characters
                body = whitespace_chars_regex.sub(' ', body)

                body = ' '.join([el for el in body.split(' ') if el not in stop_words_arr and len(el) > 0])

            text_arr.extend(body.split(' '))
            times_arr.append(time)

    return text_arr, times_arr


def filter_sentence():
	'''
	    A method to show off the filtering/cleaning that is done on a
	    comment when "filter=True" in the "extract_text_from_comments" method
	'''

    body = "Ha.  But actually no!!!  \"These are $*%# ideas. My dogs and cacti are much better than you and your goddesses and cats - I 100 percent believe they're more terrible than mine.\"\n\nhttps://imright.org/yourewrong/123456789"

    stop_words_arr = read_csv("../Data/stopwords.csv")[0]
    stop_words_arr.append('source')
    punctuation_translator = str.maketrans(' ', ' ', string.punctuation)
    url_regex = re.compile(r'\[?\(?https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)\]?\)?')
    num_regex = re.compile(r'[0-9]+')
    whitespace_chars_regex = re.compile(r'[\n\r\t]+')

    print("Original sentence:\n\t{}\n".format(body))

    body = body.lower()
    print("Lowercase:\n\t{}\n".format(body))

    # Remove all URLs from comments
    body = url_regex.sub('', body)
    print("Remove URL:\n\t{}\n".format(body))

    # Remove all numbers from comments
    body = num_regex.sub('', body)
    print("Remove numbers:\n\t{}\n".format(body))

    # Remove all punctuation from comments
    body = body.translate(punctuation_translator)
    print("Remove punctuation:\n\t{}\n".format(body))

    # Remove all special whitespace characters
    body = whitespace_chars_regex.sub(' ', body)
    print("Remove whitespace:\n\t{}\n".format(body))

    words = []
    for el in body.split(' '):
    	if el not in stop_words_arr and len(el) > 0:
    		words.append(el)
    body = ' '.join(words)
    print("Remove stopwards:\n\t{}\n".format(body))

    body = nat_lang_sentence(body)
    print("Lemmatized:\n\t{}\n".format(body))

    print("Final sentence:\n\t{}".format(body))


def get_top_n_words_from_text(text_arr, replace_with_synonyms=False, n=-1):
    '''
        text_arr is an array of strings that will be converted to
        a dictionary sorted by the integer value representing
        how many times each unique string appears in the array.

        Returns top n occuring strings as an array of duples in
        the form (string, num_occurrences).
    '''
    start = time.perf_counter()
    num_replacements = 0
    nrc = NRCReader()
    nrc.load()
    dictionary = dict()
    print("Grabbing top words...")
    total_replaced = 0
    total_obj = 0;
    for sentence in text_arr:
        words = word_tokenize(sentence)
        total_obj += 1
        if replace_with_synonyms:
            dictionary, num_replaced = replace_word_with_NRC_synonym(words, nrc, dictionary)
            total_replaced += num_replaced
        else:
            for word in words:
                if word in dictionary.keys():
                    dictionary[word] += 1
                else:
                    dictionary[word] = 1

    print("Replaced {} words.".format(total_replaced))
    print("Found {} unique words.".format(len(dictionary.keys())))
    end = time.perf_counter()
    print("Finding words took {} seconds, which is {} seconds per line".format(end-start, (end-start)/total_obj))

    sorted_words_arr = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    if n < 0:
        return sorted_words_arr[:(len(dictionary))]

    return sorted_words_arr[:n]


def get_top_n_bigrams_from_text(text_arr, replace_with_synonyms=False, n=-1):
    '''
        text_arr is an array of strings that will be converted to
        a dictionary sorted by the integer value representing
        how many times each unique string appears in the array.

        Returns top n occuring strings (bigrams) as an array of
        duples in the form (string, num_occurrences).
    '''
    start = time.perf_counter()
    dictionary = dict()
    print("Grabbing top bigrams...")
    total_obj = 0;
    for sentence in text_arr:
        words = word_tokenize(sentence)
        bigrams = nltk.bigrams(words)
        for bg in bigrams:
            bigram = ' '.join(bg)
            if bigram in dictionary.keys():
                dictionary[bigram] += 1
            else:
                dictionary[bigram] = 1

    print("Found {} unique bigrams.".format(len(dictionary.keys())))
    end = time.perf_counter()
    print("Finding bigrams took {} seconds".format(end-start))

    sorted_bigrams_arr = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)

    if n < 0:
        return sorted_bigrams_arr[:(len(dictionary))]

    return sorted_bigrams_arr[:n]


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


def match_words_with_emotion(input_file, filt=False,output_file="words_with_count_and_emotions.json"):
    '''
        Takes an input_file of comments, extracts the text (and filters, if needed),
        then finds the NRC words and their counts throughout all comments
    '''

    start = time.perf_counter()
    print("Reading input file: {}".format(input_file))
    text_arr, times_arr = extract_text_from_comments(input_file, filt)

    lemmatize_start = time.perf_counter()
    print("Lemmatizing sentences...")
    text_arr = list(map(nat_lang_sentence, text_arr))
    print("Lemmatized the sentences - took {} seconds".format(time.perf_counter()-lemmatize_start))
    num_sentences = len(text_arr)

    # Set second parameter to True if you want non-NRC words to
    # be replaced by their respective NRC synonyms. Otherwise, False
    all_words = get_top_n_words_from_text(text_arr, False)

    text_arr = None
    nrc = NRCReader()
    nrc.load()

    # Only grabbing words in NRC
    nrc_words = [el for el in all_words if el[0] in nrc.data.keys()]
    filtered_file = open(output_file, 'w')

    print("Finding emotions for words")
    for w in nrc_words:
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

    print("Finished. Took {} seconds".format((time.perf_counter() - start)))
    filtered_file.close()

    random_data_path = '{}-information.txt'.format(output_file.split('.')[0])
    rd_file = open(random_data_path, 'w')

    rd_file.write("Total comments read: {}\n".format(num_sentences))
    rd_file.write("Total unique words: {}\n".format(len(all_words)))
    rd_file.write("Total NRC words founds: {}\n\n".format(len(nrc_words)))
    presidential_names = ['donald', 'trump', 'hillary', 'clinton']
    presidential_counts = [el for el in all_words if el[0] in presidential_names]
    rd_file.write("Counts for candidates:\n")
    rd_file.write("\t {} : {}\n".format(presidential_counts[0][0], presidential_counts[0][1]))
    rd_file.write("\t {} : {}\n".format(presidential_counts[1][0], presidential_counts[1][1]))
    rd_file.write("\t {} : {}\n".format(presidential_counts[2][0], presidential_counts[2][1]))
    rd_file.write("\t {} : {}\n\n".format(presidential_counts[3][0], presidential_counts[3][1]))
    rd_file.write("Top 1000 words overall (not just NRA):\n")
    top_1000_words = all_words[:1000]
    for word in top_1000_words:
        rd_file.write("\t{}\n".format(word))

    rd_file.close()
    print("Created files: {}, {}\n".format(output_file, random_data_path))


def get_utc_days():
	'''
	    Gives an array of duples containg the start and end of each
	    day in UTC time from October 26 to November 23
	'''

    # First day is 1477501200 to 1477544400 (only 12 hours)
    first_day = [1477501200,1477544400]
    # Last day is 1479880800 to 1479924000 (only 12 hours)
    last_day = [1479880800,1479924000]

    # Starting at beginning of second day
    days = [first_day]
    utc_time = 1477544400

    while utc_time < 1479880800:
        
        if utc_time == 1478408400:
            # Daylight savings??
            days.append([utc_time, (utc_time+90000)])
            utc_time += 90000
        else:
            days.append([utc_time, (utc_time+86400)])
            utc_time += 86400

    days.append(last_day)
    return days


def get_string_date_of_utc(number):
    date_strings = ['October 26','October 27','October 28','October 29','October 30',
    'October 31','November 1','November 2','November 3','November 4','November 5',
    'November 6','November 7','November 8','November 9','November 10','November 11',
    'November 12','November 13','November 14','November 15','November 16','November 17',
    'November 18','November 19','November 20','November 21','November 22','November 23']

    utc_dates = get_utc_days()
    utc_string_date = ''

    for i in range(0,len(utc_dates)):
        if number >= utc_dates[i][0] and number < utc_dates[i][1]:
            utc_string_date = date_strings[i]
            break

    return utc_string_date


def grab_data_from_days(input_file, days=None):
	'''
	    input file should be the full dataset of comments, or
	    some data set that has the data for the days you are looking at

	    our data files for each day are all named in the same format,
	    so this allows you to easily grab the data from each one

	    days is in form [ [1477501200,1477544400] , [1479880800,1479924000] , ...]
	    days must be in order
	'''
    file = open(input_file, 'r')
    if days == None:
        days = get_utc_days()

    for day in days:
        date_string = '-'.join(get_string_date_of_utc(day[0]+(86400/4)).split(' '))
        path = '{}-data.json'.format(date_string)
        date_file = open(path, 'w')
        utc = 0;

        while utc < day[1]:
            line = file.readline()

            if len(line) == 0:
                break

            data = json.loads(line)
            utc = data['created_utc']

            if utc < day[0] or utc >= day[1]:
                continue

            json.dump(data, date_file)
            date_file.write('\n')

        date_file.close()
        print("Created file: {}".format(path))


def grab_words_from_days(days=None):
	'''
	    all of our data (by day) is named in the same way, and this allows you
	    to easily grab the words from each one
	    
	    days is in form [ [1477501200,1477544400] , [1479880800,1479924000] , ...]
	    days must be in order
	'''
    if days == None:
        days = get_utc_days()

    for day in days:
        date_string = '-'.join(get_string_date_of_utc(day[0]+(86400/4)).split(' '))
        input_file = '{}-data.json'.format(date_string)
        output_file = '{}-nrc-words.json'.format(date_string)
        match_words_with_emotion(input_file, True, output_file)


def grab_bigrams_from_day(days=None):
    if days == None:
        days = get_utc_days()

    for day in days:
        date_string = '-'.join(get_string_date_of_utc(day[0]+(86400/4)).split(' '))
        input_file = '{}-data.json'.format(date_string)
        output_file = '{}-bigrams.json'.format(date_string)

        print("Reading input file: {}".format(input_file))
        text_arr, times_arr = extract_text_from_comments(input_file, True)

        bigrams = get_top_n_bigrams_from_text(text_arr)
        bigrams = [el for el in bigrams if el[1] > 100]

        filtered_file = open(output_file, 'w')
        for bg in bigrams:
            bigram = {'bigram': bg[0], 'count': bg[1]}
            json.dump(bigram, filtered_file)
            filtered_file.write('\n')
        filtered_file.close()
        print("Created file: {}".format(output_file))


def split_words_by_emotion(input_file, output_file='split_words_by_emotion.json'):
    file = open(input_file, 'r')

    emotions = ['anger','anticipation','disgust','fear','joy',
                'negative','positive','sadness','surprise','trust']

    output_data =   {
                        'anger': {},
                        'anticipation': {},
                        'disgust': {},
                        'fear': {},
                        'joy': {},
                        'negative': {},
                        'positive': {},
                        'sadness': {},
                        'surprise': {},
                        'trust': {} 
                    }

    while True:
        line = file.readline()

        if len(line) == 0:
            break

        data = json.loads(line)
        word = data['word']
        count = data['count']
        word_emotions = data['emotions']

        for e in emotions:
            if word_emotions[e] == 1:
                word_and_count = { 'word': word, 'count': count }
                output_data[e][word] = count

    filtered_file = open(output_file, 'w')
    json.dump(output_data, filtered_file)
    filtered_file.close()
    print("Created file: {}".format(output_file))


def split_emotion_by_day(days=None):
    if days == None:
        days = get_utc_days()

    for day in days:
        date_string = '-'.join(get_string_date_of_utc(day[0]+(86400/4)).split(' '))
        input_file = '{}-nrc-words.json'.format(date_string)
        output_file = '{}-emotions.json'.format(date_string)
        split_words_by_emotion(input_file, output_file)


def nat_lang_word(word):
    '''Word lemmatizer; find the root of the word. E.g. 'dogs' becomes 'dog'''
    return lmt.lemmatize(word)


def nat_lang_sentence(sentence):
    new_words = list(map(nat_lang_word, sentence.split(' ')))
    return ' '.join(new_words)


def replace_word_with_NRC_synonym(words, nrc, dictionary):
    # Only replace nouns with nouns, vowels with vowels etc.
    tagged = nltk.pos_tag(words)
    num_replaced = 0
    for i in range(0,len(words)):
        if words[i] in dictionary.keys() or words[i] in nrc.data.keys():
            if words[i] in dictionary.keys():
                dictionary[words[i]] += 1
            else:
                dictionary[words[i]] = 1
        else:
            replacements = []
            for syn in nltk.corpus.wordnet.synsets(words[i]):

                # Do not attempt to replace proper nouns or determiners
                if tagged[i][1] == 'NNP' or tagged[i][1] == 'DT':
                    break
                
                # The tokenizer returns strings like NNP, VBP etc
                # but the wordnet synonyms has tags like .n.
                # So we extract the first character from NNP ie n
                # then we check if the dictionary word has a .n. or not 
                word_type = tagged[i][1][0].lower()
                if syn.name().find("."+word_type+"."):
                    # extract the word only
                    r = syn.name()[0:syn.name().find(".")]
                    replacements.append(r)

            replacements = [el for el in replacements if el in dictionary.keys() or el in nrc.data.keys()]
            if len(replacements) > 0:
                num_replaced += 1
                new_word = replacements[randint(0,len(replacements)-1)]
                if new_word in dictionary.keys():
                    dictionary[new_word] += 1
                else:
                    dictionary[new_word] = 1
 
            else:
                dictionary[words[i]] = 1

    return dictionary, num_replaced


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
