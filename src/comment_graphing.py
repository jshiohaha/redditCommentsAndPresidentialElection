import pprint, operator, sys, json, string

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import pygal 
from PIL import Image
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from utils import extract_text_from_comments, aggregate_comments_by_day, read_csv, get_utc_days, get_string_date_of_utc


def plot_word_cloud(input_file, image_input_file):
    '''
        The input_file must be comprised of only text. An example
        of acceptable input is the manuscript of a book. 
    '''
    # read the mask image data
    image_mask_file = image_input_file
    image_mask = np.array(Image.open(image_mask_file))

    stopwords = set(STOPWORDS)
    stopwords.add("said")
    stopwords.add("source")

    wc = WordCloud(background_color="white", max_words=2000, mask=image_mask,
                   stopwords=stopwords)

    # generate word cloud
    wc.generate(open(input_file).read())

    # manually compute output file from input file and store result there
    output_file = "{}-output.png".format(input_file.split(".")[0])
    wc.to_file(output_file)

    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.figure()
    plt.imshow(image_mask, cmap=plt.cm.gray, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def plot_sentiment_overtime(input_file, output_file):
    comments_by_subbredit = dict()
    data = read_csv(input_file, header=True, append_data=True)

    comments_by_subbredit = dict(zip(data[0], [[] for _ in range(len(data[0]))]))
    keys = list(comments_by_subbredit.keys())
    dates = []

    for i in range(1, len(data)):
        for k in range(0, len(keys)):
            if k < 1 :
                dates.append(data[i][k])
                print(data[i][k])
            else:
                comments_by_subbredit[keys[k]].append(float(data[i][k]))

    line_chart = pygal.Line(x_label_rotation=20)
    line_chart.title = 'Average Compound Sentiment Score by Subreddit'

    # dates = [ dates[i].split(" ")[1] if i % 5 == 0 else " " for i in range(len(dates))]
    dates = [ dates[i] if i % 2 == 0 else " " for i in range(len(dates))]

    line_chart.x_labels = dates

    for k, v in comments_by_subbredit.items():
        if k == 'Date':
            continue

        line_chart.add(str(k), list(v))

    line_chart.render_to_file(output_file)


def plot_emotion_dot_chart():
    date_strings = ['October 26','October 27','October 28','October 29','October 30',
    'October 31','November 1','November 2','November 3','November 4','November 5',
    'November 6','November 7','November 8','November 9','November 10','November 11',
    'November 12','November 13','November 14','November 15','November 16','November 17',
    'November 18','November 19','November 20','November 21','November 22','November 23']

    input_files = []
    for day in date_strings:
        date_string = '-'.join(day.split(' '))
        input_file = '{}-emotions.json'.format(date_string)
        input_files.append(input_file)

    dot_chart = pygal.Dot(x_label_rotation=30)
    dot_chart.title = 'Daily Emotion'
    
    dot_chart.x_labels = date_strings

    emotions = ['anger','anticipation','disgust','fear','joy','sadness','surprise','trust','positive','negative']

    dictionary = dict()

    for em in emotions:
        dictionary[em] = []

    for f in input_files:
        file = open(f, 'r')
        data = json.loads(file.readline())
        file.close()

        for em in emotions:
            dictionary[em].append(sum(data[em].values()))

    # norm = mpl.colors.Normalize(vmin=-1.,vmax=1.)

    for key in dictionary.keys():
        dot_chart.add(key, dictionary[key])

    dot_chart.render_to_file('../Images/Emotion/All-Emotions.svg')


def plot_emotion_growth_pie_chart():
    emotions = ['anger','anticipation','disgust','fear','joy','sadness','surprise','trust','positive','negative']
    date_strings = ['October 26','October 27','October 28','October 29','October 30',
    'October 31','November 1','November 2','November 3','November 4','November 5',
    'November 6','November 7']

    input_files = []
    for day in date_strings:
        date_string = '-'.join(day.split(' '))
        input_file = '{}-emotions.json'.format(date_string)
        input_files.append(input_file)

    bar_chart = pygal.Bar()
    bar_chart.title = 'Emotion Growth Before/After Election'
    bar_chart.x_labels = ['October 26 to November 7', 'November 9 to November 23']

    dictionary = dict()
    growth_rates = dict()
    for em in emotions:
        dictionary[em] = []
        growth_rates[em] = []

    for f in input_files:
        file = open(f, 'r')
        line = file.readline()
        data = json.loads(line)
        file.close()

        for em in emotions:
            dictionary[em].append(sum(data[em].values()))

    for key in dictionary.keys():
        growth_rate = (max(dictionary[key]) - min(dictionary[key]))/max(dictionary[key])
        growth_rates[key].append(growth_rate)

    date_strings = ['November 9','November 10','November 11','November 12','November 13','November 14','November 15','November 16','November 17',
    'November 18','November 19','November 20','November 21','November 22','November 23']
    input_files = []
    for day in date_strings:
        date_string = '-'.join(day.split(' '))
        input_file = '{}-emotions.json'.format(date_string)
        input_files.append(input_file)

    for f in input_files:
        file = open(f, 'r')
        line = file.readline()
        data = json.loads(line)
        file.close()

        for em in emotions:
            dictionary[em].append(sum(data[em].values()))

    for key in dictionary.keys():
        growth_rate = (max(dictionary[key]) - min(dictionary[key]))/max(dictionary[key])
        growth_rates[key].append(growth_rate)
        bar_chart.add(key, growth_rates[key])

    bar_chart.render_to_file('../Images/Emotion/Growth-Rate.svg')


def plot_emotion_pie_chart(input_file):
    emotions = ['anger','anticipation','disgust','fear','joy','sadness','surprise','trust']

    date_string = "{} {}".format(input_file.split('-')[0], input_file.split('-')[1])

    pie_chart = pygal.Pie(inner_radius=.4)
    pie_chart.title = 'Emotion on {} (in %)'.format(date_string)

    file = open(input_file, 'r')
    line = file.readline()
    data = json.loads(line)
    file.close()

    for em in emotions:
        count = sum(data[em].values())
        pie_chart.add(em, count)

    pie_chart.render_to_file('../Images/Emotion/{}.svg'.format(input_file))
    print("Created emotion pie chart for {}".format(date_string))


def plot_emotion_pie_chart_days(days=None):
    if days == None:
        days = get_utc_days()

    for day in days:
        date_string = '-'.join(get_string_date_of_utc(day[0]+(86400/4)).split(' '))
        input_file = '{}-emotions.json'.format(date_string)
        plot_emotion_pie_chart(input_file)


def plot_heatmap_of_words(input_file, popular_words, specific_subreddit=None):
    '''

        Example of popular_words param:

        popular_words = ['trump','people','vote','hillary','clinton','election','bernie','time',
                         'years','good','president','country','voted','make','party','won',
                         'candidate','shit','america','states','fuck','dnc','better','lost','obama']
    '''
    text, times = extract_text_from_comments(input_file, filter=True, specific_subreddit=specific_subreddit)
    comments_and_dates_by_day = aggregate_comments_by_day(text, times, group_by="hours", group_by_const=1)

    date = list()
    word = list()
    score = list()
    for element in comments_and_dates_by_day:
        time, text = element

        print("Time: {}".format(time))

        if text is not None:
            text = " ".join(text).split(" ")

            keys = Counter(text).keys()
            values = Counter(text).values()
            total = sum(values)
            values = [round((v/total), 3) for v in values]

            aggregated_list = [el for el in list(zip(keys, values)) if el[0] in popular_words]
            sorted_words_arr = sorted(aggregated_list, key=operator.itemgetter(1), reverse=True)

            for i in range(len(sorted_words_arr)):
                date.append(time)
                word.append(sorted_words_arr[i][0])
                score.append(sorted_words_arr[i][1])

    df = pd.DataFrame({ 'Word':word, 'Day':date, 'Score':score})
    # might be doing some sort of unintended sorting on date
    comments = df.pivot("Word", "Day", "Score")

    ax = sns.heatmap(comments)
    plt.show()
