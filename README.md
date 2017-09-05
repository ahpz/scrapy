# scrapy
从 instagram youtube twitter 网站抓取电商网站信息(Foot Locker、Alpha Industries, Inc.、Eastbay、New Moosejaw LLC、pixiemarket.com)数据 , 注意：需要一个能够访问国外对应网站的机器，如果是走代理。则需要研究源码修改代理设置

示例:
python instagram.py eastbay 抓取电商网站eastbay 的instagram账号 中视频和图片信息 

python tweet.py eastbay 抓取电商网站 

python youtube.py eastbay 搜索youtube 网站eastbay 关键词相关视频（下载4-20分钟的视频） 由于采用关键词搜索后下载 存在一定得误差

注意依赖工具:pip install twitter pip install python-twitter
