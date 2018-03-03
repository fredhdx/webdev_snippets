import requests
import os, sys
import codecs

url = "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=88805253&pagesize=30&tid=0&page=1&keyword=&order=pubdate"
content = requests.get(url).json()
pages = content['data']['pages']

with codecs.open('vlist.txt', 'w', encoding='utf-8') as f:
    for i in range(1, pages + 1):
        print("getting page " + str(i))
        uri = "https://space.bilibili.com/ajax/member/getSubmitVideos?mid=88805253&pagesize=30&tid=0&keyword=&order=pubdate" + "&page=" + str(i)
        try:
            content = requests.get(uri).json()
            vlist = content['data']['vlist']
            for video in vlist:
                title = video['title'].strip()
                aid = video['aid']
                url = "https://www.bilibili.com/video/av" + str(aid)
                f.write('# ' + title + os.linesep)
                f.write(url + os.linesep)
        except Exception:
            print(Exception)
            sys.exit
