#coding:utf-8


import requests
from urllib import parse
from bs4 import BeautifulSoup
from os import path
import json
import sys
import configparser
import hashlib
from multiprocessing.dummy import Pool as ThreadPool

class Tieba(object):
    def __init__(self,BDUSS):
        self.BDUSS=BDUSS
        self.headers={'Cookie':'BDUSS='+self.BDUSS}
        if path.exists('data.ini')==False:
            print('首次执行，正在抓取喜欢的贴吧...')
            self.saveList()

    def getRes(self,url,headers=None):
        r=requests.get(url,headers=headers)
        if r.status_code == 200:
            try:
                j=json.loads(r.text)
                return j
            except ValueError as e:
                return r.text
        else:
            raise Exception("HTTP Error:", r.status_code)
    def postRes(self,url,headers=None,data=None):
        r=requests.post(url,headers=headers,data=data,timeout=10)
        if r.status_code == 200:
            try:
                j=json.loads(r.text)
                return j
            except:
                return r.text
        else:
            raise Exception("POST Error:",r.status_code)
    def encodeData(self,data):
        '''主要是计算sign的值'''
        SIGN_KEY='tiebaclient!!!'
        s=''
        keys=data.keys()
        #print(sorted(keys))
        for i in sorted(keys):
            s+=i+'='+data[i]
        sign=hashlib.md5((s+SIGN_KEY).encode('utf-8')).hexdigest().upper()
        #print(sign)
        data.update({'sign':str(sign)})
        return data
#签到基本函数
    def sign(self,kw,fid=None):
        url='http://c.tieba.baidu.com/c/c/forum/sign'
        if fid==None:
            fid=self.getfid(kw)
        data={
            'BDUSS':self.BDUSS,
            'fid':fid,
            'kw':kw,
            'tbs':self.gettbs()#'12d4181f7a12804b1471269978'
        }
        d=self.encodeData(data)
        d=parse.urlencode(d)
        d=d.encode('utf-8')
        res=self.postRes(url,self.headers,d)
        if res["error_code"]=='0':
            msg='√'
        elif res["error_code"]=='160002':
            msg='已经签到过了'
        else:
            msg='×'
        print("签到",kw,"吧\t",msg)
        return res

    def multiSign(self):
        like=self.getLike()
        print('共需签到%d个贴吧'% len(like))
        pool=ThreadPool(4)
        result=pool.map(self.sign,like)
        pool.close()
        pool.join()
    def getfid_web(self,kw):
        fid_url='http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname='+parse.quote(kw)
        fid=self.getRes(fid_url)['data']['fid']
        return str(fid)

    def getfid(self,kw):
        config=configparser.ConfigParser()
        config.read('data.ini',encoding='utf-8')
        try:
            fid=config.get('fid',kw)
        except:
            fid=self.getfid_web(kw)
        return fid

    def gettbs(self):
        url='http://tieba.baidu.com/dc/common/tbs'
        tbs=self.getRes(url,self.headers)
        return str(tbs['tbs'])


    def saveList(self):
        print('正在抓取喜欢的贴吧...')
        url='http://tieba.baidu.com/mo/q---B8D06B9EB00241F919F47789D4FD3103%3AFG%3D1--1-1-0--2--wapp_1385540291997_626/m?tn=bdFBW&tab=favorite'
        text=self.getRes(url,headers=self.headers)
        soup=BeautifulSoup(text,"html.parser")
        a=soup.select('div.d a')
        config=configparser.ConfigParser()
        config['fid']={}
        length=len(a)
        for i in range(length):
            sys.stdout.write('收集数据：'+str(int(i*100/length))+'%\r')
            sys.stdout.flush()
            config['fid'][a[i].get_text()]=self.getfid(a[i].get_text())
        with open('data.ini','w',encoding='utf-8') as configfile:
            config.write(configfile)
            print('写入文件成功！')

    def getLike(self):
        config=configparser.ConfigParser()
        config.read('data.ini',encoding='utf-8')
        like=config.options('fid')
        return like






BDUSS='手动BDUSS๑乛◡乛๑'
t=Tieba(BDUSS)


t.multiSign()

