import pprint, operator, sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from PIL import Image
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from utils import extract_text_from_comments, aggregate_comments_by_day


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


def plot_heatmap_of_words(input_file, popular_words):
    '''

        Example of popular_words param:

        popular_words = ['trump','people','vote','hillary','clinton','election','bernie','time',
                         'years','good','president','country','voted','make','party','won',
                         'candidate','shit','america','states','fuck','dnc','better','lost','obama']
    '''
    text, times = extract_text_from_comments(input_file, filter=True)
    comments_and_dates_by_day = aggregate_comments_by_day(text, times, group_by="days", group_by_const=1)

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
