import sys
import bz2
import json
import csv

''' Example json object from reddit file...

    {  
        - "author":"Dethcola",
        "author_flair_css_class":"",
        "author_flair_text":"Clairemont",
        - "body":"A quarry",
        "can_gild":true,
        "controversiality":0,
        - "created_utc":1506816000,
        "distinguished":null,
        "edited":false,
        "gilded":0,
        "id":"dnqik14",
        "is_submitter":false,
        "link_id":"t3_73ieyz",
        "parent_id":"t3_73ieyz",
        "permalink":"/r/sandiego/comments/73ieyz/best_place_for_granite_counter_tops/dnqik14/",
        "retrieved_on":1509189606,
        - "score":3,
        "stickied":false,
        - "subreddit":"sandiego",
        - "subreddit_id":"t5_2qq2q"
    }
'''

def filter_compressed_comments_file(input_file, output_file):
    '''
        takes a binary input file of Reddit Comments and filters them based on time,
        author, then subreddit (found in '../Data/PoliticalSubreddits.csv')

        input_file is either All-Comments-2016-10.bz2 or All-Comments-2016-11.bz2
        output_file is where you want the newly filtered data to be outputted
    '''
    list_of_subreddits = create_political_subreddits_list('../Data/PoliticalSubreddits.csv')
    with open(subbreddits) as file:
        lines = file.readlines()
        list_of_subreddits = lines[0].split(',')

    filtered_file = open(output_file, 'w')
    bz_file = bz2.BZ2File(input_file, 'rb', 1000000)
    total_obj, written_obj = 0, 0

    while True:
        total_obj += 1
        line = bz_file.readline().decode('utf8')

        if len(line) == 0:
            break

        data = json.loads(line)

        # oct 26 utc date: 1477501200, november 23 utc date: 1479924000
        start = 1477501200
        end = 1479924000
        created_on = data['created_utc']
        if created_on < start or created_on > end:
            continue

        # do not save if author = [deleted], 'AutoModerator', contains bot
        author = data['author'].lower()
        if author == '[deleted]' or author == 'automoderator' or 'bot' in author: 
            continue

        subreddit = data['subreddit']
        if subreddit not in list_of_subreddits:
            continue

        output_data = {
            'author': data['author'],
            'body': data['body'],
            'created_utc': int(float(data['created_utc'])),
            'score': int(data['score']),
            'subreddit': data['subreddit'],
            'subreddit_id': data['subreddit_id']
        }

        json.dump(output_data, filtered_file)
        filtered_file.write('\n')

        written_obj += 1

    print('Total objects: {}'.format(total_obj))
    print('Written objects: {}'.format(written_obj))

    bz_file.close()
    filtered_file.close()


def create_political_subreddits_list(input_file):
    subbreddits = "PoliticalSubreddits.csv"
    list_of_subreddits = []

    with open(subbreddits) as file:
        lines = file.readlines()
        list_of_subreddits = lines[0].split(',')

    return list_of_subreddits


def parse_compressed_moderator_file(input_file):
    '''
        input_file is the path to the moderators.gz file,
        which is the compressed file containing the list
        of all known moderators on reddit across all
        subreddits.
    '''
    list_of_subreddits = create_political_subreddits_list('../Data/PoliticalSubreddits.csv')
    gz_file = gzip.open(input_file, 'rb')
    moderator_authors = []

    while True:
        line = gz_file.readline()

        if len(line) == 0:
            break

        data = json.loads(line)

        subreddit = data['subreddit']
        if subreddit not in list_of_subreddits:
            continue

        for j in data['moderators']:
            moderator_authors.append(j['name'])

    gz_file.close()
    return moderator_authors


def filter_known_moderators_from_comments_file(input_file, output_file):
    moderator_authors = parse_compressed_moderator_file('../Data/moderators.gz')
    filtered_file = open(output_file, "w")

    total_obj = 0
    written_obj = 0

    with open(input_file) as f:
        for line in f:
            data = json.loads(line)
            total_obj += 1

            body = data['body']
            author = data['author']
            if author in moderator_authors and (('comment' in body or 'submission' in body) and 'removed' in body):
                continue

            json.dump(data, filtered_file)
            filtered_file.write('\n')

            written_obj += 1

    filtered_file.close()
    print('Total objects: {}'.format(total_obj))
    print('Written objects: {}'.format(written_obj))

