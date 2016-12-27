# -*- coding: utf-8 -*- 
from urllib import request,parse
import json
import re
import hashlib
import threading
from os import path
import sys

class Tieba(object):
    def __init__(self,BDUSS):
        self.BDUSS=BDUSS
        #self.userinfo=self.getUserInfo()
        #self.signlist=self.getSignlist()
        if path.exists('list.txt')==False:
            print('首次执行，正在抓取喜欢的贴吧...')
            self.saveList()


#抓取数据(基本)
    def fetch(self,url,BDUSS=None,data=None):
        req=request.Request(url)
        if BDUSS:
            req.add_header('Cookie','BDUSS='+BDUSS)
        with request.urlopen(req,data=data) as f:
            data=f.read()
            try:
                res=data.decode('utf-8')
            except UnicodeDecodeError as e:
                res=data.decode('gbk')
            #如果可以json编码，则返回json编码后的内容.否则返回网页文本内容
            try:
                j=json.loads(res)
                return j
            except ValueError as e:
                return res

    def getfid(self,kw):
        fid_url='http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname='+parse.quote(kw)
        fid=self.fetch(fid_url)['data']['fid']
        return str(fid)

    def gettbs(self):
        url='http://tieba.baidu.com/dc/common/tbs'
        tbs=self.fetch(url,self.BDUSS)['tbs']
        return str(tbs)

    def getUserInfo(self):
        url='http://tieba.baidu.com/f/user/json_userinfo'
        data=self.fetch(url,self.BDUSS)
        return data

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

#获得喜欢的贴吧列表
    def getLike(self):
        like=[]
        url='http://tieba.baidu.com/f/like/mylike?&pn='
        d=self.fetch(url,self.BDUSS)
        #关注的贴吧不满一页的话
        try:
            page_pattern=re.compile('pn=(.*)">尾页</a>')
            page=page_pattern.search(d).groups()[0]
            page=int(page)
        except AttributeError:
            page=1
        for i in range(page):
            u=url+str(i+1)
            d=self.fetch(u,self.BDUSS)
            pattern_table = re.compile('<table>(.*)</table>')
            res_table = pattern_table.search(d).groups()
            table=res_table[0]
            a=table.split('</tr>')
            a.pop(0)
            a.pop()  #去除最后的空值
            for i in range(len(a)):
                pattern_data = re.compile('''title=".*">(.*)</a></td><td><a class="cur_exp"''')
                res_data = pattern_data.search(a[i]).groups()
                like.append(res_data[0])
        #print(like,len(like))
        return like

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
        res=self.fetch(url,self.BDUSS,d)
        return res

#写数据
    def saveList(self):
        with open('list.txt','w',encoding='utf-8') as f:
            list=self.getLike()
            length=len(list)
            list_fid=[]
            for i in range(length):
                list_fid.append(None)
            for i in range(length):
                #print(round(i/len(list),2),'\r')
                sys.stdout.write('收集数据：'+str(int(i*100/length))+'%\r')
                sys.stdout.flush()
                list_fid[i]=[list[i],self.getfid(list[i])]
            f.write(str(list_fid))
            print('写入文件成功！')

#读数据
    def readList(self):
        with open('list.txt','r',encoding='utf-8') as f:
            d=f.readlines()
        for i in range(len(d)):
            d[i]=eval(d[i])
        return d[0]
