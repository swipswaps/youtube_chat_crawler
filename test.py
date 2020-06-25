#!/usr/bin/env python3
test = '<script>window["ytInitialData"] = {"responseContext":{"serviceTrackingParams":[{"service":"CSI","params":[{"key":"GetLiveChatReplay_rid","value":"0xb2f8b07452d1f5df"},{"key":"c","value":"WEB"},{"key":"cver","value":"2.20200624.03.00"},{"key":"yt_li","value":"0"}]},"'
if 'window["s"]' in test:
    print('FOUNDIT')
