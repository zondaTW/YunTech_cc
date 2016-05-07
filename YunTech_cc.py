# -*- coding: utf-8 -*-
import sys  
from PySide.QtGui import *  
from PySide.QtCore import *  
from PySide.QtWebKit import *
from PySide.QtNetwork import *
from bs4 import BeautifulSoup
import requests
from PIL import Image
import cStringIO
import os
import time

class MyNetworkAccessManager(QNetworkAccessManager):
    def __init__(self, url):
        QNetworkAccessManager.__init__(self)
        self.request = QNetworkRequest(QUrl(url))
		#設定header
        self.request.setRawHeader('User-agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0')
        self.request.setRawHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        self.request.setRawHeader("Accept-Language", "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3")
        self.request.setRawHeader("Accept-Encoding", "gzip, deflate, br")
        self.request.setRawHeader("Referer", "https://webapp.yuntech.edu.tw/YunTechSSO")
        self.request.setRawHeader("Connection", "close")
        self.reply = self.get(self.request)

    def createRequest(self, operation, request, data):
        #print "mymanager handles ", request.url()
        return QNetworkAccessManager.createRequest( self, operation, request, data )

#Take this class for granted.Just use result of rendering.
class Render(QWebPage):  
    def __init__(self):  
        self.app = QApplication(sys.argv)  
        QWebPage.__init__(self)
        
        self.loadFinished.connect(self._loadFinished)
        manager = MyNetworkAccessManager(url)
        self.setNetworkAccessManager(manager)
   
    def _loadFinished(self, result):  
        self.frame = self.mainFrame()  
        self.app.quit()

    def load_page_get(self, url):
        self.mainFrame().load(QUrl(url))
        self.app.exec_()  

    def load_page_post(self, url, user, pwd, secret):
		#傳值(post)
        post_data = QByteArray()
        post_data.append('ReturnUrl=%2FYunTechSSO&pStandardSubmit=false')
        post_data.append('&pLoginName=' + user)
        post_data.append('&pLoginPassword=' + pwd)
        post_data.append('&pSecretString=' + secret)
        self.mainFrame().load(QNetworkRequest(QUrl(url)), QNetworkAccessManager.PostOperation, post_data)
        self.app.exec_()    
    
    def new_load_page_get(self, url, v = False):
        self.va = v	#判斷現在是否在抓驗證圖片
        self.mainFrame().load(QUrl(url))
        self.connect(self, SIGNAL("loadFinished(bool)"), self._getimage)
        self.app.exec_()
        
    def _getimage(self, result):
        if not result:
            print "Request failed"
        print 'start'
        self.setViewportSize(self.mainFrame().contentsSize())
        image = QImage(self.viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self.mainFrame().render(painter)
        painter.end()
        page_image = QImage(image.scaled(5000, 5000))   #擷取網頁畫面
        if self.va:
            ValidationImage = page_image.copy(0, 0, 630, 200)         #只切割驗證圖片
            self.va = False
            if ValidationImage.save("ValidationImage.png"):
                print "V~~~~OK"
        else:
            if page_image.save("page.png"):
                print "P~~~~OK"
              
base_url = 'https://webapp.yuntech.edu.tw/YunTechSSO'
login = '/Account/Login'
home = '/Home/Index'

r = Render()
r.new_load_page_get(base_url + login)
result = r.frame.toHtml()
soup = BeautifulSoup(result.encode('utf-8'), "lxml")

with open('tt1.txt', 'w') as f:
    f.write(result.encode('utf-8'))


#抓取驗證碼圖片的網址
image_url = soup.find('div', {'class':'grid_8 omega'}).find('img', {'id':'ValidationImage'}).get('src')
image_url = image_url[image_url.index("/YunTechSSO")+11:]
r.new_load_page_get(base_url + image_url, True)

#print r.networkAccessManager().cookieJar().allCookies()
user = raw_input('Enter username: ')
pwd = raw_input('Enter password: ')
secret = raw_input('Enter secret: ')

# 登入
r.load_page_post(base_url + login, user, pwd, secret)
result = r.frame.toHtml()
soup = BeautifulSoup(result.encode('utf-8'), "lxml")
print "2----------------------------"
print soup

# 登入成功後Index頁面
r.new_load_page_get(base_url + home)
result = r.frame.toHtml()
soup = BeautifulSoup(result.encode('utf-8'), "lxml")
print "3----------------------------"

with open('tt2.txt', 'w') as f:
    f.write(result.encode('utf-8'))

