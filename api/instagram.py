# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import signal
import argparse
import datetime
import requests
import threading

from skeleton.bootstrap import Env
from skeleton.libs.threadpool_lib import CThreadPool

"""instagram网站信息抓"""

def enum(**enums):
    return type('Enum', (), enums)

Quality = enum(Thumbnail = 'thumbnail', Low = 'low_resolution', Standard = 'standard_resolution')

"""多线程任务函数"""
def download(url, file_path):
    with open(file_path, 'wb') as file:
        sys.stdout.write("Downloading %s \n" % os.path.basename(file_path))
        bytes = requests.get(url).content
        file.write(bytes)
                
def sig_handler(sig, frame):   
    sys.stdout.write('receive a signal %d \n' % (sig))
    sys.exit(0)
    
    
class InstaCrawler(object):

    quality   = Quality.Standard #选择 何种标准的图片 或者 视频
    user_name = ''
    
    def __init__(self, user_name, quality=Quality.Standard):
        self.user_name   = user_name
        self.quality     = quality
        self.thread_pool = CThreadPool()
        self.max_num     = 100 #0; #一千个数据
        self.save_dir = os.path.join(Env.base_path, u'data/instagram', self.user_name.replace(' ',''), time.strftime("%Y%m%d", time.localtime()))

    def __del__(self):
        self.thread_pool.close() #优雅关闭多线程
        
    def stop(self):
        self.thread_pool.close()
        
    def is_over(self):
        if 0 == self.thread_pool.thread_num():
            return True
        return False
    
    
    """https://www.instagram.com/officialeastbay/media/"""
    """https://github.com/su23/InstagramCrawler/blob/master/InstaCrawler.py"""
    def async_start(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        items = self.crawl()
        sys.stdout.write("count of items:{0}\n".format(len(items)))
        filename = os.path.join(self.save_dir, 'results')
        fp = open(filename, 'w+')
        """多线程失败 待优化"""
        for item in items:
            
                
            url = item['image_url'] #standard_resolution
            base_name = url.split('/')[-1]
            file_path = os.path.join(self.save_dir, base_name) #多线程下载存储本地文件
            item['image_filepath'] = file_path
            args  = (url, file_path) #待验证 多线程 是否可以恨自己访问当前类的 变量 应该可以
            self.thread_pool.run(download, args = args) #线程池添加job
            
            if 'video' == item['type']:
                url = item['video_url'] #standard_resolution
                base_name = url.split('/')[-1]
                file_path = os.path.join(self.save_dir, base_name) #多线程下载存储本地文件
                item['video_filepath'] = file_path 
                args  = (url, file_path) #待验证 多线程 是否可以恨自己访问当前类的 变量 应该可以
                self.thread_pool.run(download, args = args) #线程池添加job
                               
                
            fp.write(json.dumps(items) + '\n') #本地文件存储
            
            
        fp.close()
        
    
    
    def crawl(self, items=[], max_id=None):
        url    = 'http://instagram.com/' + self.user_name + '/media' + ('?&max_id=' + max_id if max_id is not None else '')
        medias = json.loads(requests.get(url).text)

        #items.extend([ curr_item for curr_item in media['items'] ])
        """存储特定数据"""
        for media in medias['items']:
            Env.get_logger().debug("media:{0}".format(json.dumps(media)))
            if u'video' != media['type'] and u'image' != media['type']:
                Env.output("The type not video or image | type:{0}".format(media['type'])) #例如type = carousel
                Env.get_logger().debug("The type not video or image | type:{0}".format(media['type']))  
                continue;            
            item = {}
            item['id']           = media['id']
            item['created_time'] = media['created_time']
            item['text']         = media['caption']['text']
            item['like_count']   = media['likes']['count']
            item['comment_count']= media['comments']['count']
            item['image_url']    = media['images'][self.quality]['url']
            item['type']         = media['type'] #video or image
            if 'video' == media['type']:
                item['video_url'] = media['videos'][self.quality]['url']
                item['video_views']=media['video_views']
            items.append(item)
            
            

        if 'more_available' not in medias or medias['more_available'] is False or len(items) > self.max_num:
            return items
        else:
            max_id = medias['items'][-1]['id']
            return self.crawl(items, max_id)
        

        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('username', default="officialeastbay")
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, sig_handler)  
    signal.signal(signal.SIGINT, sig_handler)     
    """注意 父进程会挂起等待子线程结束 因为子线程未设置setdaemon"""
    try:
        insta = InstaCrawler(args.username)
        insta.async_start()
        insta.stop()
    except Exception as e:
        Env.output("exception:{0}".format(repr(e)))
        Env.get_logger().error("exception:{0}".format(repr(e)))
    else:
        while insta.is_over():
            """保证主线程不挂起 可以处理信号"""
            time.sleep(1)
            
        Env.output("success.");
        Env.get_logger().debug("success download instagram") 
        