# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import types
import signal
import urllib2
import argparse
import datetime
import requests
import threading

from urllib2 import URLError, HTTPError

from skeleton.bootstrap import Env
from skeleton.libs.youtube_lib import CYoutube
from skeleton.libs.youtube_lib import YoutubeAPI
from skeleton.libs.threadpool_lib import CThreadPool

#谷歌开发者 账号密钥 注意有效期...待定
CONSUMER_KEY = 'xxxxxxxxxx'


def enum(**enums):
    return type('Enum', (), enums)

Quality = enum(Default = 'default', High = 'high', Medium = 'medium')


"""线程函数:下载视频或者图片"""
def download(url, file_path):
    with open(file_path, 'wb') as file:
        sys.stdout.write("Downloading %s \n" % os.path.basename(file_path))
        bytes = requests.get(url).content
        file.write(bytes)
"""线程函数:下载youtube视频 解析网页 分片下载"""
def download_video(url, file_path):
    try:
        youtube = CYoutube()
        youtube.get_videos(url, file_path)        
    except HTTPError as e:
        Env.output("The server couldn\'t fulfill the request| url:{0} | code:{1}".format(url, e.code))            
        Env.get_logger().warning("The server couldn\'t fulfill the request| url:{0} | code:{1}".format(url, e.code))
    except URLError as e:  
        Env.output('We failed to reach a server | url :{0} | reason:{1}'.format(url, e.reason))
        Env.get_logger().warning('We failed to reach a server | url :{0} | reason:{1}'.format(url, e.reason));
                         
    except Exception as e:
        Env.output("url:{0} | exception:{1}".format(url, repr(e)))
        Env.get_logger().warning("url {0} | exceptin:{1}".format(url, repr(e)))
    else:
        Env.output("success download youtube video :{0}".format(url))
        Env.get_logger().debug("success download youtube video :{0}".format(url))        
    
    
    
def sig_handler(sig, frame):   
    sys.stdout.write('receive a signal %d \n' % (sig))
    sys.exit(0)
    
class YoutubeCrawler(object):
    
    quality   = Quality.Default
    
    def __init__(self, keyword = u'eastbay'):
        self.api     = YoutubeAPI({'key':CONSUMER_KEY})
        
        self.max_num = 100 #0   #下载前1000 视频 实际下载>1000    
        self.keyword = keyword
        self.page_size = 20;
        self.thread_pool = CThreadPool()
        self.save_dir  = os.path.join(Env.base_path, u'data/youtube', keyword.replace(' ',''), time.strftime("%Y%m%d", time.localtime()))
        self.params    =  {
            'q'               : self.keyword,
            'type'            :'video', #channel,palylist,video
            'part'            :'id, snippet',
            'maxResults'      : self.page_size,  #0 - 50 default 5
            "videoType"       :'episode', 
            'videoDuration'   :'medium', #保证视频文件不会很大 4-20min
            #'videoCaption'    :'closedCaption', #有caption的视频 此参数会导致返回值 为空 
            'videoDimension'  :'2d',
        };
    def __del__(self):
        self.thread_pool.close() #优雅关闭多线程
           
    def stop(self):
        self.thread_pool.close()
           
    def is_over(self):
        if 0 == self.thread_pool.thread_num():
            return True
        return False  
    
    """https://developers.google.com/youtube/v3/docs/search/list"""
    def async_start(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        items = self.crawl()
        sys.stdout.write("count of items:{0}\n".format(len(items)))
        filename = os.path.join(self.save_dir, 'results')
        fp = open(filename, 'w+')
        """多线程失败 待优化"""        
        for item in items:
            url = item['image_url']
            base_name = item['id'] + '.jpg'
            file_path = os.path.join(self.save_dir, base_name) #多线程下载存储本地文件
            item['image_filepath'] = file_path 
            args  = (url, file_path) #待验证 多线程 是否可以恨自己访问当前类的 变量 应该可以
            self.thread_pool.run(download, args = args) #线程池添加job
            """下载视频文件 使用CYoutube"""
            url = item['video_url']
            base_name = item['id'] + '.mp4'#使用video_id 作为视频文件名
            file_path = os.path.join(self.save_dir, base_name)
            args = (url, file_path)
            self.thread_pool.run(download_video, args) #多线程下载视频
            fp.write(json.dumps(items) + '\n') #本地文件存储
        
        fp.close()
            
    """视频频繁getRating待优化 根据搜索视频ID 搜索视频列表"""
    def crawl(self, items = [], token = None):
        videos = self.api.paginate_results(self.params, token)
        Env.get_logger().debug('videos:{0}'.format(json.dumps(videos)))
        for video in videos['results']:
            Env.get_logger().debug("video:{0}".format(json.dumps(video)))
            item = {}
            if u'youtube#video' != video['id']['kind']:
                Env.output("The type not youtube video.")
                Env.get_logger().warning("The type not youtube video.")
                Env.get_logger().warning("item :{0}".format(json.dumps(video)))
                continue;
            item['id']    = video['id']['videoId']
            item['text']  = video['snippet']['title'] #video['description'] description 中含有url
            item['type']  = video['id']['kind']
            item['created_time'] = video['snippet']['publishedAt']
            item['image_url'] = video['snippet']['thumbnails'][self.quality]['url']
            item['video_url'] = u'https://www.youtube.com/watch?v={0}'.format(item['id']) #使用特殊CYoutube 下载视频 非
            items.append(item)
            
        """无数据 或者 已经达到下载上线 则停止继续查询 nextPageToken=null"""
        if videos.has_key(u'info') and videos[u'info'].has_key(u'nextPageToken') and not videos[u'info'][u'nextPageToken'] and len(items) < self.max_num:
            page_token = videos[u'info'][u'nextPageToken']
            return self.crawl(items, page_token)
        else:
            return items
            
        
if __name__ == "__main__":
    pass
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('keyword', default="eastbay")
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, sig_handler)  
    signal.signal(signal.SIGINT, sig_handler)     
    """注意 父进程会挂起等待子线程结束 因为子线程未设置setdaemon"""
    try:
        youtube = YoutubeCrawler(args.keyword)
        youtube.async_start()
        youtube.stop()
    except Exception as e:
        Env.output("exception:{0}".format(repr(e)))
        Env.get_logger().error("exception:{0}".format(repr(e)))
    else:
        while youtube.is_over():
            """保证主线程不挂起 可以处理信号"""
            time.sleep(1)
            
        Env.output("success.");
        Env.get_logger().debug("success download youtbube")     
        
        
    
