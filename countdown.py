from __future__ import division, print_function
from ConfigParser import SafeConfigParser
from datetime import datetime
from HTMLParser import HTMLParser
from praw import Reddit
import time
import re


def compute_time_ago_params(target):
    countdown_delta = target - datetime.now()
    days = countdown_delta.days
    hours = (countdown_delta.seconds // 3600) + 1  # add one hour to be able to show "less than"
    minutes = 61 + ((countdown_delta.seconds - (hours * 3600)) // 60)  # because of the above operation for hours, subtract from 61 to get "less than"
    # seconds = (countdown_delta.seconds - (hours * 3600) - (minutes * 60))

    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
    }

def update_countdown(username, password, subreddit_name, target):
    user_agent = '/r/{0} countdown'.format(subreddit_name)
    reddit = Reddit(user_agent)
    reddit.login(username, password, disable_warning=True)

    # reddit access
    subreddit = reddit.get_subreddit(subreddit_name)
    settings = subreddit.get_settings()
    description = HTMLParser().unescape(settings['description'])

    # time matches
    countdown_delta = target - datetime.now()
    days_left = countdown_delta.days
    hours_left = countdown_delta.seconds // 3600

    # regex and strings
    # countdownSearch = re.compile("(\[\d?\d?\]\([#][a-z]*\)\s[a-z]*[!]?\s?)+", re.I)  # old regex
    countdownSearch = re.compile("((\s([a-z]{4})*)*\s?\[\d?\d?\]\([#][a-z]*\)\s[a-z]*[!]?\s?)+", re.I)
    origStr = " less than [](#days) days [](#hours) hours\n"
    noDaysStr = " less than [](#hours) hours\n"
    noHoursStr = " less than [](#minutes) minutes\n"
    raceLiveStr = " [](#days) Racing [](#hours) is [](#minutes) live\n"
    updatemeStr = " [](#days) Current [](#hours) event [](#minutes) ended\n"

    # make sure our event hasn't happened yet
    if target > datetime.now():

        if days_left > 0:
            description = re.sub(countdownSearch, origStr, description)
        elif hours_left > 0 and days_left == 0:
            description = re.sub(countdownSearch, noDaysStr, description)
        else:
            description = re.sub(countdownSearch, noHoursStr, description)

        for key, value in compute_time_ago_params(target).iteritems():
            pattern = "\\[[^\\]]*\\]\\(#{0}\\)".format(key)  # replace [<anything>](#<key>)
            repl = "[{0}](#{1})".format(value, key)  # with [<value>](#<key>)
            description = re.sub(pattern, repl, description)

    # if race is happening, show raceLiveStr, else race is over, show updatemeStr
    else:
        countdownSearch.search(description)
        if target.hour > datetime.now().hour - 3:
            description = re.sub(countdownSearch, raceLiveStr, description)
        else:
            description = re.sub(countdownSearch, updatemeStr, description)

    subreddit.update_settings(description=description)

while True:

    if __name__ == '__main__':
        config_parser = SafeConfigParser()
        config_parser.read('countdown.cfg')

        target = config_parser.get('reddit', 'target')
        target_datetime = datetime.strptime(target, '%B %d %Y %H:%M:%S')

        update_countdown(username=config_parser.get('reddit', 'username'),
                         password=config_parser.get('reddit', 'password'),
                         subreddit_name=config_parser.get('reddit', 'subreddit'),
                         target=target_datetime)

        print("Countdown updated. Sleeping for 10 minutes")

        time.sleep(600)
