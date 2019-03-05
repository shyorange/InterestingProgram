# -*- coding=utf-8 -*-
# __author__ : "shyorange"
# __date__ :  2019/3/4

import os
import requests
"""
文件的断点续传使用场景：下载一个文件暂停后要继续下载
"""
def break_down():
    # 1：首先获得以下载的文件的大小（获得断点，字节数）。（这里以LOL下载器为例）
    downed_bytes = os.path.getsize("LOLDownloader.exe")
    
    # 2：根据断点来进行请求数据（从断点处继续下载）
    # 重要参数：headers={"Range":"bytes=%d-" % downed_bytes}, stream=True
    html = requests.get(url="XXXXXXXXXXXX",stream=True,headers={"Range":"bytes=%d-" % downed_bytes})
    
    # 3：将请求的内容追加进原文件
    with open("LOLDownloader.exe","ab") as f:
        f.write(html.content)
