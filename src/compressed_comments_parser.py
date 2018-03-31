import sys
import bz2
import json
import csv

''' Example json object from reddit file...

    {  
        "author":"Dethcola",
        "author_flair_css_class":"",
        "author_flair_text":"Clairemont",
        "body":"A quarry",
        "can_gild":true,
        "controversiality":0,
        "created_utc":1506816000,
        "distinguished":null,
        "edited":false,
        "gilded":0,
        "id":"dnqik14",
        "is_submitter":false,
        "link_id":"t3_73ieyz",
        "parent_id":"t3_73ieyz",
        "permalink":"/r/sandiego/comments/73ieyz/best_place_for_granite_counter_tops/dnqik14/",
        "retrieved_on":1509189606,
        "score":3,
        "stickied":false,
        "subreddit":"sandiego",
        "subreddit_id":"t5_2qq2q"
    }
'''

def main():
    subbreddits = "Data/PoliticalSubreddits.csv"
    list_of_subreddits = []
    with open(subbreddits) as file:
        lines = file.readlines()
        list_of_subreddits = lines[0].split(',')

    filename = "Data/SampleData/RC_2007-01.bz2"

    bz_file = bz2.BZ2File(filename, 'rb', 1000000)

    # figure out later
    output_filename = "Data/Output/output.json"
    filtered_file = open(output_filename, "w")

    total_obj, written_obj = 0, 0
    while True:
        total_obj += 1
        line = bz_file.readline().decode('utf8')

        if len(line) == 0:
            break

        data = json.loads(line)

        # oct 26 utc date: 1477501200
        # november 23 utc date: 1479924000
        start = 1477501200
        end = 1479924000
        created_on = data["created_utc"]
        if created_on < start or created_on > end:
            continue

        # author will be [deleted] if the comment was deleted
        # author is moderator if is 'AutoModerator'
        # author name contains bot
        author = data["author"].lower()
        if author == '[deleted]' or author == 'automoderator' or "bot" in author: 
            continue

        subreddit = data["subreddit"]
        if subreddit not in list_of_subreddits:
            continue

        # write current json object data to output file
        json.dump(data, filtered_file)
        filtered_file.write("\n")

        written_obj += 1

    print("Total objects: {}".format(total_obj))
    print("Written objects: {}".format(written_obj))

    bz_file.close()
    filtered_file.close()

if __name__ == '__main__':
    main()