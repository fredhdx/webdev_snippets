#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import psutil
import sys
import os
from bs4 import BeautifulSoup
import multiprocessing
from multiprocessing import cpu_count
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
from pandas import DataFrame
import gevent.monkey
import gevent.pool as gpool

from timeit import Timer


def limit_cpu():
    "is called at every process start"
    p = psutil.Process(os.getpid())
    # set to lowest priority, this is windows only, on Unix use ps.nice(19)
    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

def timefunc(f):
    '''
    Time profiling function adapted from "Simple Timers" example at
    https://zapier.com/engineering/profiling-python-boss/
    '''
    def f_timer(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        elapsed_time = end - start
        print(f.__name__ + ' took ' + str(elapsed_time) + ' seconds')
        return (result, elapsed_time)
    return f_timer

def json_video(v_dict):
    ''' parse single item in json['data']['vlist']
        output: {'title', 'aid', 'url'}
    '''
    title = v_dict['title']
    aid = v_dict['aid']
    url = "https://www.bilibili.com/video/av" + str(aid)

    return {'title':title, 'aid': aid, 'url': url}

def get_pageList(mid, headers):
    ''' input: (bilibili) mid
        output: A list containing page urls for all submitted videos
    '''
    pageSize = 30
    API= ('https://space.bilibili.com/ajax/member/getSubmitVideos?mid=%s' % str(mid)
            + '&pagesize=%s' % str(pageSize) + '&tid=0&page=%s&keyword=&order=pubdate' )
    pageNum = 0
    itemNum = 0

    # get pageNum
    try:
        r = requests.get((API % '1'), headers=headers)
        if r.status_code == 200:
            json_content = r.json()
            tlist = json_content['data']['tlist']
            for tab in tlist:
                itemNum += int(tlist[tab]['count'])
            pageNum = int(itemNum/pageSize) + (itemNum % pageSize > 0)
    except Exception as e:
        print(e)
        sys.exit

    # get page list
    API_list = [(API % str(page)) for page in range(1, pageNum + 1)]
    return [API_list, itemNum]

def get_singlePage(params):

    page_url, headers = params

    try:
        r = requests.get(page_url, headers=headers)
        json_content = r.json()
        vlist = json_content['data']['vlist']
        records = []
        for video in vlist:
            records.append(json_video(video))
    except Exception as e:
        print(e)
        sys.exit

    return records

def get_singlePage_session(params):
    page_url, session = params

    try:
        r = session.get(page_url)
        json_content = r.json()
        vlist = json_content['data']['vlist']
        records = []
        for video in vlist:
            records.append(json_video(video))
    except Exception as e:
        print(e)
        sys.exit

    return records

@timefunc
def parseAll_pool(API_list, numProcess, headers):
    print(len(API_list))
    with multiprocessing.Pool(numProcess, limit_cpu) as p:
        result = p.map(get_singlePage, zip(API_list, [headers] * len(API_list)))

@timefunc
def parseAll_pool_session(API_list, numProcess, headers):
    s = requests.session()
    s.headers.update(headers)
    with multiprocessing.Pool(numProcess, limit_cpu) as p:
        result = p.map(get_singlePage_session, zip(API_list, [s] * len(API_list)))

    s.close()

@timefunc
def parseAll_gevent(API_list, numProcess, headers):
    gevent.monkey.patch_socket()
    pool = gpool.Pool(numProcess)

    for i in range(len(API_list)):
        pool.spawn(get_singlePage, (API_list[i], headers))

    pool.join()

@timefunc
def parseAll_gevent_session(API_list, numProcess, headers):
    gevent.monkey.patch_socket()
    pool = gpool.Pool(numProcess)

    s = requests.session()
    s.headers.update(headers)

    for i in range(len(API_list)):
        pool.spawn(get_singlePage_session, (API_list[i], s))

    pool.join()

    s.close()

def exception_handler(request, exception):
    print("Request failed")

@timefunc
def parseAll_grequests(API_List, numProcess, headers):
    import grequests
    s = requests.Session()

    rs = (grequests.get(u, session=s) for u in API_List)
    responses = grequests.map(rs, exception_handler=exception_handler)
    all_records = []

    for r in responses:
        if r:
            if r.status_code == 200:
                json_content = r.json()
                vlist = json_content['data']['vlist']
                records = []
                for video in vlist:
                    records.append(json_video(video))
                all_records += records
            else:
                print(r.status_code)

@timefunc
def parseAll_single(API_list, numProcess, headers):
    # numProcess is dummy

    result = []
    for API_url in API_list:
        result.append(get_singlePage((API_url, headers)))

def plotPerformance(performance_results, figureName):
    df = DataFrame(performance_results)
    g = sns.factorplot(x='N', y='seconds', hue='method', data=df, size=7, ci=None)
    g.set_axis_labels('N (# http requests)', 'Total Time to Complete (seconds)')
    plt.title('Performance of different http request methods vs. number of http requests')
    plt.savefig(figureName + 'png')

def simulateCrawlMember(my_func, method_name, headers):
    mid_bucket = [17221410, 2139573, 37694382, 26810901, 26480852, 1315101]
    numProcess = 10

    times = []
    for mid in mid_bucket:
        [API_list, itemNum] = get_pageList(mid, headers)
        secs = my_func(API_list, numProcess, headers)[1]
        times.append({'method': method_name, 'N': itemNum, 'seconds': secs})

    return times

def benchmark():
    sns.set_style('whitegrid')

    performance_results_all = []
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

    performance_results = simulateCrawlMember(parseAll_gevent, 'gevent', headers)
    plotPerformance(performance_results, 'gevent')
    performance_results_all += performance_results
    time.sleep(5)

    performance_results = simulateCrawlMember(parseAll_pool, 'pool', headers)
    plotPerformance(performance_results, 'pool')
    performance_results_all += performance_results
    time.sleep(5)

    performance_results = simulateCrawlMember(parseAll_gevent_session, 'gevent + Session', headers)
    plotPerformance(performance_results, 'gevent + Session')
    performance_results_all += performance_results
    time.sleep(5)

    performance_results = simulateCrawlMember(parseAll_pool_session, 'pool + Session', headers)
    plotPerformance(performance_results, 'pool + Session')
    performance_results_all += performance_results
    time.sleep(5)

    performance_results = simulateCrawlMember(parseAll_single, 'Single', headers)
    plotPerformance(performance_results,'Single' )
    performance_results_all += performance_results

    plotPerformance(performance_results_all,'Compare' )




def benchmark_timeit(number=1):
    gevent.monkey.patch_socket()
    sns.set_style('whitegrid')

    mid = 26480852
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

    API_list = get_pageList(mid, headers)

    t1 = Timer(lambda: parseAll_pool(API_list, 10, headers))
    t2 = Timer(lambda: parseAll_pool_session(API_list, 10, headers))
    t3 = Timer(lambda: parseAll_single(API_list, 10, headers))

    #for numProcess in [5, 10, 15, 20]:
    #    t1 = Timer(lambda: parse(API_list, numProcess, headers))
    #    print(t1.timeit(number=number))

    #t2 = Timer(lambda: parse_single(API_list, headers))

    print("Timed parseAll_pool: %s" % t1.timeit(number=number))
    print("Timed parseAll_pool_session: %s" % t2.timeit(number=number))
    print("Timed parseAll_single: %s" % t3.timeit(number=number))