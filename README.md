# Reddit Political Subreddit Comments during the 2016 U.S. Presidential Election

Introduction
Contents of this README

View the presentation for this project [here](http://bit.ly/2JbFA1S).

## Process Outline

### Data Acquition and Cleaning
##### Acquisition

We downloaded all Reddit comments during the months of October (RC_2016-10.bz2) and November (RC_2016-11.bz2) 2016 from [pushshift](http://files.pushshift.io/reddit/comments/). The compressed files contain a collection of JSON objects representing reddit comments. Here is an example of the JSON object: 

```{JSON}
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
```

The size of the zipped files are approximately 6.45 GB. Additionally, there are 71,826,554 JSON objects and 54,129,644 JSON objects in October and November, respectively. 

##### Cleaning - Phase I

The cleaning of the downloaded data sets include multiple phases due to the magnitude of the data sets. The first phase of filtering is meant to decrease the size of the data set by selecting comments from 2 weeks before election day (November 9) to 2 weeks after election day. Additionally, we only keep comments that were posted in the list of [political subreddits](https://github.com/jShiohaha/redditCommentsAndPresidentialElection/blob/master/Data/PoliticalSubreddits.csv). Lastly, during the initial data set filtering, we remove comments posted by authors with the names of `[deleted]` and `AutoModerator`, or authors with a name that contains `bots`.

##### Cleaning - Phase II
- remove additional subreddit moderators from a known [list of moderators](http://files.pushshift.io/reddit/moderators/).
  - Removing comments from known mods removed 233 comments 
- predict whether or not comments are a bot using [Reddit-Bot-Predictor](https://github.com/pushshift/Reddit-Bot-Detector).

### Sentiment Analysis

### Emotion Analysis
