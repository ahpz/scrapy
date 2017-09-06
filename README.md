

示例:

抓取 https://twitter.com/Eastbay 视频图片信息
python tweet.py eastbay

抓取 https://www.instagram.com/officialeastbay/ 视频图片信息
python instagram.py eastbay

抓取 youtube 网站eastbay关键词视频信息(4-40min)
python youtube.py eastbay


python 依赖:
pip install twitter 
pip install python-twitter 
pip install requests 
...其他需要的自行安装

使用注意事项:

1  配置 conf 中dev.ini 相关的日志路径log_path 和程序基本路径配置 base_url

2  使用twitter 和 youtube 时。需要申请 google 账号(https://developers.google.com/youtube) 和 twitter账号（https://apps.twitter.com/）
