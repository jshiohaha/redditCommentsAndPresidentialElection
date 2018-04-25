import pprint, operator, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import pygal 
from PIL import Image
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from utils import extract_text_from_comments, aggregate_comments_by_day, read_csv


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


def plot_word_frequencies_bar_chart(input_file):

    line_chart = pygal.Bar()
    line_chart.title = 'Browser usage evolution (in %)'
    line_chart.x_labels = map(str, range(2002, 2013))
    line_chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    line_chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
    line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,    9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])
    line_chart.render_to_file('../Images/output.svg')


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
