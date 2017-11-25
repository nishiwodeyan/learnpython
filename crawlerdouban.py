#!/usr/bin/env python
# encoding: utf-8

'''
    爬取豆瓣top250 电影 信息
'''

import requests;
import thread
from bs4 import BeautifulSoup;
import os;
import time;
import threading;

'''
   定义一个类 属性包含图片的名称以及下载的url
'''
class Picture:
    def __init__(self,picName,picSrcUrl):
        self.picName = picName;
        self.picSrcUrl = picSrcUrl;

'''
   下载图片，因为它比较耗时所以将其放在子线程中
'''
def downloadPicture(pictureList):
    fileDir = "/Users/aaa/Documents/douban/";
    if not os.path.isdir(fileDir):
        os.makedirs(fileDir);
    for index in range(len(pictureList)):
        try:
            picture = pictureList[index];
            filename = fileDir + picture.picName + ".webp";
            file = open(filename, "w");
            file.write(requests.get(picture.picSrcUrl, timeout=5).content);
            file.close();
        except:
            print picture.picSrcUrl,'下载失败'
            pass
    print "爬取耗时：", time.time().__float__()- cuttentTime.__float__() , 's';

param = "";# 后面分页时候拼接的参数
cuttentTime = time.time();
listPicture = [];
while True:
    # 请求豆瓣top250 电影的url
    baseUrl = 'https://movie.douban.com/top250' + param;
    myResponse = requests.get(baseUrl, timeout=5);
    myResponse.raise_for_status();
    responseString = myResponse.text;
    soup = BeautifulSoup(responseString, 'lxml');
    olArticle = soup.find('ol', class_='grid_view');# 获取存储文章的ol对象
    lilist = divItem = olArticle.find_all('li');
    for index in range(len(lilist)):
        # 下面是关于电影的一些信息文字信息
        divItemInfo = lilist[index].find('div', class_='info');
        divBd = divItemInfo.find('div', class_='bd');
        titleList = divItemInfo.find('div', class_='hd').a.find_all('span');
        stringTitle = '';
        # 影片的大致描述，导演、演员以及上映时间等
        strContentDescription = divBd.p.getText();
        # 影片的星级
        strRatingStar = divBd.div.find_all('span')[1].getText();
        # 影片的评价数目
        strComment = divBd.div.find_all('span')[3].getText();
        # 对于影片的一句话总结(有的没有影评所以要判空)
        if divBd.find('p', class_='quote'):
            strQuote = divBd.find('p', class_='quote').span.getText();
        # 进行电影名称的拼接，因为电影在不同的地方上映可能名字不同
        for indexTitle in range(len(titleList)):
            stringTitle = stringTitle + titleList[indexTitle].getText();
        print "电影名称："+stringTitle.encode('utf8')\
              +"\n电影星级："+strRatingStar.encode('utf8')\
              +"\n电影评价数目："+strComment.encode('utf8')\
              +"\n电影一句话总结："+strQuote.encode('utf8')\
              +"\n电影大致内容信息："+strContentDescription.encode('utf8').strip()+"\n";
        divItemPic = lilist[index].find('div', class_='pic');
        listPicture.append(Picture(divItemPic.a.img.get('alt'),divItemPic.a.img.get('src')));
    print "\n";
    divpaginator = soup.find('div', class_='paginator');# 获取底部分页的导航条
    spanNext = divpaginator.find('span', class_='next');# 获取后页
    # 如果后一页没有link，那么意味着已经到了最后一页了，所以需要跳出循环
    if not spanNext.link:
        break;
    # 获取link的某个属性，可以使用get方法
    param = spanNext.link.get('href');
'''
   在所有数据内容爬取完毕后开始一个新的线程下载图片，这里还非得用threading模块了，因为它开启的派生线程在运行时候，主线程不会退出，直至派生线程执行完毕
   但是如果派生线程被设置为守护线程，即设置setDaemon为true的话，主线程退出派生线程也就不执行了（但是这个不是我们想要的）
   如果直接使用thread模块就会存在主线程提前退出派生线程无法执行完毕，导致下载失败的情况
'''
try:
    # 需要注意的一点是 第一个参数是方法名，第二个参数一定是一个tuple元组，否则均会报错
    threadDownload = threading.Thread(target=downloadPicture, args=(listPicture,));
    threadDownload.setDaemon(False)
    threadDownload.start();
except:
    print "Error: unable to start thread"
