#coding:utf-8
#pip install python-slugify
from __future__ import print_function

import re
import os
import sys
import json
import signal
import argparse

from urlparse import unquote
import urllib2
import urllib
from slugify import slugify

#设置全局网络超时控制 下载视频 read 卡死
import socket
socket.setdefaulttimeout(10.0)


CHUNK_SIZE = 16 * 1024  # 16 Kb

ENCODING = {
    # Flash Video
    5: ["flv", "240p", "Sorenson H.263", "N/A", "0.25", "MP3", "64"],
    6: ["flv", "270p", "Sorenson H.263", "N/A", "0.8", "MP3", "64"],
    34: ["flv", "360p", "H.264", "Main", "0.5", "AAC", "128"],
    35: ["flv", "480p", "H.264", "Main", "0.8-1", "AAC", "128"],

    # 3GP
    36: ["3gp", "240p", "MPEG-4 Visual", "Simple", "0.17", "AAC", "38"],
    13: ["3gp", "N/A", "MPEG-4 Visual", "N/A", "0.5", "AAC", "N/A"],
    17: ["3gp", "144p", "MPEG-4 Visual", "Simple", "0.05", "AAC", "24"],

    # MPEG-4
    18: ["mp4", "360p", "H.264", "Baseline", "0.5", "AAC", "96"],
    22: ["mp4", "720p", "H.264", "High", "2-2.9", "AAC", "192"],
    37: ["mp4", "1080p", "H.264", "High", "3-4.3", "AAC", "192"],
    38: ["mp4", "3072p", "H.264", "High", "3.5-5", "AAC", "192"],
    82: ["mp4", "360p", "H.264", "3D", "0.5", "AAC", "96"],
    83: ["mp4", "240p", "H.264", "3D", "0.5", "AAC", "96"],
    84: ["mp4", "720p", "H.264", "3D", "2-2.9", "AAC", "152"],
    85: ["mp4", "1080p", "H.264", "3D", "2-2.9", "AAC", "152"],

    # WebM
    43: ["webm", "360p", "VP8", "N/A", "0.5", "Vorbis", "128"],
    44: ["webm", "480p", "VP8", "N/A", "1", "Vorbis", "128"],
    45: ["webm", "720p", "VP8", "N/A", "2", "Vorbis", "192"],
    46: ["webm", "1080p", "VP8", "N/A", "N/A", "Vorbis", "192"],
    100: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "128"],
    101: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "192"],
    102: ["webm", "720p", "VP8", "3D", "N/A", "Vorbis", "192"]
}

ENCODING_KEYS = (
    'extension',
    'resolution',
    'video_codec',
    'profile',
    'video_bitrate',
    'audio_codec',
    'audio_bitrate'
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

class CYoutube(object):
    pass
    def __init__(self):
        pass
    def _parse_stream_map(self, text):
        """Python's `parse_qs` can't properly decode the stream map
        containing video data so we use this instead.
        """
        videoinfo = {
            "itag":             [],
            "url":              [],
            "quality":          [],
            "fallback_host":    [],
            "s":                [],
            "type":             []
        }
    
        # Split individual videos
        videos = text.split(",")
        # Unquote the characters and split to parameters
        videos = [video.split("&") for video in videos]
    
        for video in videos:
            for kv in video:
                key, value = kv.split("=")
                videoinfo.get(key, []).append(unquote(value))
    
        return videoinfo
    
    
    def _extract_fmt(self,text):
        """YouTube does not pass you a completely valid URLencoded form, I
        suspect this is suppose to act as a deterrent.. Nothing some regulular
        expressions couldn't handle.
        :params text: The malformed data contained within each url node.
        """
        itag = re.findall('itag=(\d+)', text)
        if itag and len(itag) is 1:
            itag = int(itag[0])
            attr = ENCODING.get(itag, None)
            if not attr:
                return itag, None
            return itag, dict(zip(ENCODING_KEYS, attr))
    
    
    def get_videos(self, my_url, save_file):
        
        _fmt_values = []
        req = urllib2.Request(my_url, headers=HEADERS)
        response = urllib2.urlopen(req)
        filename = None #保存文件名
        if response:
            content = response.read().decode("utf-8")
            try:
                player_conf = content[18 + content.find("ytplayer.config = "):]
                bracket_count = 0
                for i, char in enumerate(player_conf):
                    if char == "{":
                        bracket_count += 1
                    elif char == "}":
                        bracket_count -= 1
                        if bracket_count == 0:
                            break
                else:
                    sys.stdout.write("Cannot get JSON from HTML\n")
    
                index = i + 1
                data = json.loads(player_conf[:index])
    
            except Exception as e:
                raise Exception("Cannot decode JSON: {0}".format(repr(e)))
    
    
            stream_map = self._parse_stream_map(
                data["args"]["url_encoded_fmt_stream_map"])
    
            title = slugify(data["args"]["title"])
            sys.stdout.write("Title: {0}\n".format(title))
            js_url = "http:" + data["assets"]["js"]
            video_urls = stream_map["url"]
        
        
            
            for i, url in enumerate(video_urls):
                try:
                    fmt, fmt_data = self._extract_fmt(url)
                    if fmt_data["extension"] == "mp4" and fmt_data["profile"] == "High":
                        self.download(url, save_file)
                        _fmt_values.append(fmt)
                except KeyError as e:
                    os.stdout.write("exception:{0} \n".format(repr(e)))
                    continue
        return filename
    
    def download(self, url, filename):
        req = urllib2.Request(url, headers=HEADERS)
        response = urllib2.urlopen(req, timeout=3)#待优化 有些视频有广告 需要等很久
    
        bytes_received = 0
        download_size = int(response.info().getheader("Content-Length"))
        sys.stdout.write("url:%s file:%s \n"%(url, filename))        
        with open(filename, 'wb') as dst_file:
            while True:
                _buffer = response.read(CHUNK_SIZE) 
                if not _buffer and bytes_received == download_size:
                    sys.stdout.write("Video saved: %s \n" % os.path.join(os.getcwd(), filename))
                    break
                bytes_received += len(_buffer)
                dst_file.write(_buffer)    
    

"""https://github.com/madcoda/php-youtube-api"""
class YoutubeAPI:
    youtube_key = ""

    apis = {
        'videos.list': 'https://www.googleapis.com/youtube/v3/videos',
        'search.list': 'https://www.googleapis.com/youtube/v3/search',
        'channels.list': 'https://www.googleapis.com/youtube/v3/channels',
        'playlists.list': 'https://www.googleapis.com/youtube/v3/playlists',
        'playlistItems.list': 'https://www.googleapis.com/youtube/v3/playlistItems',
        'activities': 'https://www.googleapis.com/youtube/v3/activities',
    }

    page_info = {}

    def __init__(self, params):

        if not params:
            raise ValueError('The configuration options must be an array..')

        if 'key' not in params:
            raise ValueError('Google API key is required, please visit http://code.google.com/apis/console')

        self.youtube_key = params['key']

    def get_video_info(self, video_id):

        api_url = self.get_api('videos.list')
        params = {
            'id': video_id,
            'key': self.youtube_key,
            'part': 'id, snippet, contentDetails, player, statistics, status'
        }
        apiData = self.api_get(api_url, params)

        return self.decode_single(apiData)

    def get_videos_info(self, video_ids):

        ids = video_ids
        if not isinstance(video_ids, basestring):
            ids = video_ids.join(',')

        api_url = self.get_api('videos.list')
        params = {
            'id': ids,
            'part': 'id, snippet, contentDetails, player, statistics, status'
        }
        api_data = self.api_get(api_url, params)

        return self.decode_list(api_data);

    def search(self, q, max_results=10):

        params = {
            'q': q,
            'part': 'id, snippet',
            'maxResults': max_results
        }

        return self.search_advanced(params)

    def search_videos(self, q, max_results=10, order=None, page_token = None):
        #https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=25&q=eastbay&type=video&videoDuration=short&videoType=episode&key={YOUR_API_KEY}
        params = {
            'q': q,
            'type': 'video',
            'part': 'id, snippet',
            'maxResults': max_results,
            "videoType":'episode',
            'videoDuration':'medium'
        }
        if order is not None:
            params['order'] = order
        if page_token is not None:
            params['pageToken'] = page_token

        return self.search_advanced(params)

    def search_channel_videos(self, q, channel_id, max_results=10, order=None):

        params = {
            'q': q,
            'type': 'video',
            'channelId': channel_id,
            'part': 'id, snippet',
            'maxResults': max_results
        }
        if order is not None:
            params['order'] = order

        return self.search_advanced(params)

    def search_advanced(self, params, page_info=True):

        api_url = self.get_api('search.list')
        if params is None or 'q' not in params:
            raise ValueError('at least the Search query must be supplied')

        api_data = self.api_get(api_url, params)
        if page_info:
            return {
                'results': self.decode_list(api_data),
                'info': self.page_info
            }
        else:
            return self.decode_list(api_data)

    def paginate_results(self, params, token=None):

        if token is not None:
            params['pageToken'] = token
        if params:
            return self.search_advanced(params, True)

    def get_channel_by_name(self, username, optional_params=False):

        api_url = self.get_api('channels.list')
        params = {
            'forUsername': username,
            'part': 'id,snippet,contentDetails,statistics,invideoPromotion'
        }
        if optional_params:
            params += optional_params

        api_data = self.api_get(api_url, params)
        return self.decode_single(api_data)

    def get_channel_by_id(self, id, optional_params=False):

        api_url = self.get_api('channels.list')
        params = {
            'id': id,
            'part': 'id,snippet,contentDetails,statistics,invideoPromotion'
        }
        if optional_params:
            params += optional_params

        api_data = self.api_get(api_url, params)
        return self.decode_single(api_data)

    def get_playlists_by_channel_id(self, channel_id, optional_params={}):

        api_url = self.get_api('playlists.list')
        params = {
            'channelId': channel_id,
            'part': 'id, snippet, status'
        }
        if optional_params:
            params += optional_params

        api_data = self.api_get(api_url, params)
        return self.decode_list(api_data)

    def get_playlist_by_id(self, id):

        api_url = self.get_api('playlists.list')
        params = {
            'id': id,
            'part': 'id, snippet, status'
        }
        api_data = self.api_get(api_url, params)
        return self.decode_single(api_data)

    def get_playlist_items_by_playlist_id(self, playlist_id, max_results=50):

        api_url = self.get_api('playlistItems.list')
        params = {
            'playlistId': playlist_id,
            'part': 'id, snippet, contentDetails, status',
            'maxResults': max_results
        }
        api_data = self.api_get(api_url, params)
        return self.decode_list(api_data)

    def get_activities_by_channel_id(self, channel_id):

        if channel_id is None:
            raise ValueError('ChannelId must be supplied')

        api_url = self.get_api('activities')
        params = {
            'channelId': channel_id,
            'part': 'id, snippet, contentDetails'
        }
        api_data = self.api_get(api_url, params)
        return self.decode_list(api_data)

    def parse_vid_from_url(self, youtube_url):

        if 'youtube.com' in youtube_url:
            params = self._parse_url_query(youtube_url)
            return params['v']
        elif 'youtu.be' in youtube_url:
            path = self._parse_url_path(youtube_url)
            vid = path[1:]
            return vid
        else:
            raise Exception('The supplied URL does not look like a Youtube URL')

    def get_channel_from_url(self, youtube_url):

        if 'youtube.com' not in youtube_url:
            raise Exception('The supplied URL does not look like a Youtube URL')
        path = self._parse_url_path(youtube_url)
        if '/channel' in path:
            segments = path.split('/')
            channel_id = segments[len(segments) - 1]
            channel = self.get_channel_by_id(channel_id)
        elif '/user' in path:
            segments = path.split('/')
            username = segments[len(segments) - 1]
            channel = self.get_channel_by_name(username)
        else:
            raise Exception('The supplied URL does not look like a Youtube Channel URL')

        return channel

    def get_api(self, name):
        return self.apis[name]

    def decode_single(self, api_data):

        res_obj = json.loads(api_data)
        if 'error' in res_obj:
            msg = "Error " + res_obj['error']['code'] + " " + res_obj['error']['message']
            if res_obj['error']['errors'][0]:
                msg = msg + " : " + res_obj['error']['errors'][0]['reason']
            raise Exception(msg)
        else:
            items_array = res_obj['items']
            if isinstance(items_array, dict) or len(items_array) == 0:
                return False
            else:
                return items_array[0]

    def decode_list(self, api_data):

        res_obj = json.loads(api_data)
        if 'error' in res_obj:
            msg = "Error " + res_obj['error']['code'] + " " + res_obj['error']['message']
            if res_obj['error']['errors'][0]:
                msg = msg + " : " + res_obj['error']['errors'][0]['reason']
            raise Exception(msg)
        else:
            self.page_info = {
                'resultsPerPage': res_obj['pageInfo']['resultsPerPage'],
                'totalResults': res_obj['pageInfo']['totalResults'],
                'kind': res_obj['kind'],
                'etag': res_obj['etag'],
                'prevPageToken': None,
                'nextPageToken': None
            }
            if 'prevPageToken' in res_obj:
                self.page_info['prevPageToken'] = res_obj['prevPageToken']
            if 'nextPageToken' in res_obj:
                self.page_info['nextPageToken'] = res_obj['nextPageToken']

            items_array = res_obj['items']
            if isinstance(items_array, dict): #if isinstance(items_array, dict) or len(items_array) == 0: 注意 params中某些参数会导致 items=[]
                return False
            else:
                return items_array

    def api_get(self, url, params):

        params['key'] = self.youtube_key

        f = urllib2.urlopen(url + "?" + urllib.urlencode(params))
        data = f.read()
        f.close()

        return data

    def _parse_url_path(self, url):

        array = urlparse(url)
        return array['path']

    def _parse_url_query(self, url):

        array = urlparse(url)
        query = array['query']
        query_parts = query.split('&')
        params = {}
        for param in query_parts:
            item = param.split('=')
            if not item[1]:
                params[item[0]] = ''
            else:
                params[item[0]] = item[1]

        return params


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, required=False,
                       help='file with video urls separated by newlines')
    parser.add_argument("-u", "--url", type=str, required=False,
                       help='URL to YouTube video')
    parser.add_argument("-c", "--chunksize", type=int, required=False,
                       help="increase the chunksize (Kb), 16Kb is default (e.g. --chunksize 1024 would be 1 mb) ")
    args = parser.parse_args()

    if args.chunksize:
        CHUNK_SIZE = args.chunksize * 1024  # in Kbs

    #signal.signal(signal.SIGINT, signal_handler)
    obj = CYoutube();
    if args.file:
        with open(args.file) as f:
           urls = f.readlines()

        for my_url in urls:
            try:
                filename = my_url.split('=')[-1] #videoId
                obj.get_videos(my_url, filename)
                print("Done!")
            except ValueError:
                print("Url not correct:{}".format(my_url))

    elif args.url:
        try:
            filename = args.url.split('=')[-1]
            obj.get_videos(args.url, filename)
            print("Done!")
        except ValueError:
            print("Url not correct:{}".format(my_url))
