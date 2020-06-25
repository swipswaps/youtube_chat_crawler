# YouTube Chat Crawler

This Python script crawls and saves live chat messages from finished YouTube livestreams.

This is a fork from [kkorona/youtube_chat_crawler](https://github.com/kkorona/youtube_chat_crawler), which is itself bundled [from a blog post](http://watagassy.hatenablog.com/entry/2018/10/08/132939) from 雑記帳 (@watagasi).

You must have Python 3.x installed on your system, and have the following requirements installed (e.g. via `pip3 install`):

  - `bs4`
  - `lxml`
  - `request`
  - `ast` (should be part of stdlib)

## Usage

Run the command:

    ./YoutubeChatReplayCrawler.py YOUTUBE_VIDEO_URL

This dumps a json file to the current directory, containing all the stream data.

## Converting the JSON to text

Run the command:

    python3 chatReplayConverter.py

And all the .json files in the current directory will be converted into an easy-to-read text file form.
