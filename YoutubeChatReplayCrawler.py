#!/usr/bin/env python3

from bs4 import BeautifulSoup
import ast
import requests
import re
import sys
import pprint

# Verify user supplied a YouTube URL.
if len(sys.argv) == 1:
    print("Usage : YoutubeChatReplayCrawler.py {Target Youtube URL} to crawl chat replays of Target Youtube URL.");
    sys.exit(0);

# Set up variables for requests.
target_url = sys.argv[1]
dict_str = ""
next_url = ""
comment_data = []
session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

# Get the video page.
html = session.get(target_url)
soup = BeautifulSoup(html.text, "html.parser")

# Produce a valid filename (from Django text utils).
def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

# Retrieve the title and sanitize so it is a valid filename.
title = soup.find_all("title")
title = title[0].text.replace(" - YouTube","")
title = get_valid_filename(title)

# Regex match for emoji.
RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)

# Find any live_chat_replay elements, get URL for next live chat message.
for iframe in soup.find_all("iframe"):
    if("live_chat_replay" in iframe["src"]):
        next_url= iframe["src"]

if not next_url:
    print("Couldn't find live_chat_replay iframe. Maybe try running again?");
    sys.exit(1);

# TODO - We should fail fast if next_url is empty, otherwise you get error:
# Invalid URL '': No schema supplied. Perhaps you meant http://?

# TODO - This loop is fragile. It loops endlessly when some exceptions are hit.
while(1):

    try:
        html = session.get(next_url, headers=headers)
        soup = BeautifulSoup(html.text,"lxml")

        # Loop through all script tags.
        for script in soup.find_all("script"):
            script_text = str(script)
            if 'ytInitialData' in script_text:
                dict_str = ''.join(script_text.split(" = ")[1:])

        # Capitalize booleans so JSON is valid Python dict.
        dict_str = dict_str.replace("false","False")
        dict_str = dict_str.replace("true","True")

        # Strip extra HTML from JSON.
        dict_str = re.sub(r'};.*\n.+<\/script>', '}', dict_str)

        # Correct some characters.
        dict_str = dict_str.rstrip("  \n;")

        # TODO: I don't seem to have any issues with emoji in the messages.
        # dict_str = RE_EMOJI.sub(r'', dict_str)

        # Evaluate the cleaned up JSON into a python dict.
        dics = ast.literal_eval(dict_str)

        # "https://www.youtube.com/live_chat_replay?continuation=" + continue_url が次のlive_chat_replayのurl
        # TODO: On the last pass this returns KeyError since there are no more
        # continuations or actions. Should probably just break in that case.
        continue_url = dics["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]
        print('Found another live chat continuation:')
        print(continue_url)
        next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url
        # dics["continuationContents"]["liveChatContinuation"]["actions"]がコメントデータのリスト。先頭はノイズデータなので[1:]で保存
        for samp in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
            comment_data.append(str(samp)+"\n")

    # next_urlが入手できなくなったら終わり
    except requests.ConnectionError as e:
        print("Connection Error")
        continue
    except requests.HTTPError as e:
        print("HTTPError")
        break
    except requests.Timeout as e:
        print("Timeout")
        continue
    except requests.exceptions.RequestException as e:
        print(e)
        break
    except KeyError as e:
        error = str(e)
        if 'liveChatReplayContinuationData' in error:
            print('Hit last live chat segment, finishing job.')
        else:
            print("KeyError")
            print(e)
        break
    except SyntaxError as e:
        print("SyntaxError")
        print(e)
        break
        # continue #TODO
    except KeyboardInterrupt as e:
        break
    except :
        print("Unexpected error:" + str(sys.exc_info()[0]))

# Write the comment data to a file named after the title of the video.
with open(title + ".json", mode='w', encoding="utf-8") as f:
    f.writelines(comment_data)

print('Comment data saved to ' + title + '.json')
