# -*- coding:utf-8 -*-
from urllib import request,parse
import json
import re
import hashlib
from os import path

class Tieba(object):
    def __init__(self,BDUSS):
        self.BDUSS=BDUS
        
    def tidyLikeData(self,data):
        '''整理抓取的我喜欢的贴吧页面'''
        likeData=[]
        #取出table中的内容
        pattern_table = re.compile('<table class="tb" width="100%">(.*)</table>')
        res_table = pattern_table.search(data).groups()
        table=res_table[0]
        a=table.split('</tr>')
        a.pop()  #去除最后的空值
        for i in range(len(a)):
            pattern_data = re.compile('<a href=".*">(.*)</a>.*等级(.*)</td><td.*经验值(.*)</td>')
            res_data = pattern_data.search(a[i]).groups()
            likeData.append({'kw':res_data[0],'level':res_data[1],'exp':res_data[2]})
        return likeData

    def tieba_fetch(self,url,header=None,data=None):
        '''
        参数：url，header(只需要传入BDUSS)，data
        返回值：json或string
        '''
        req=request.Request(url)
        if header:
            req.add_header('Cookie','BDUSS='+header)
        with request.urlopen(req,data=data) as f:
            res=f.read().decode('utf-8')
            #如果可以json编码，则返回json编码后的内容
            #否则返回网页文本内容
            try:
                j=json.loads(res)
                return j
            except json.decoder.JSONDecodeError as e:
                #print('except:', e)
                return res

    def getfid(self,kw):
        fid_url='http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname='+parse.quote(kw)
        #print(fid_url)
        fid=self.tieba_fetch(fid_url)['data']['fid']
        #print(fid)
        return str(fid)

    def urlen(self,data):
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

    def sign(self,kw,fid=None):
        url='http://c.tieba.baidu.com/c/c/forum/sign'
        if fid==None:
            fid=self.getfid(kw)
        data={
        'BDUSS':self.BDUSS,
        'fid':fid,
        'kw':kw,
        'tbs':'12d4181f7a12804b1471269978'
        }
        d=self.urlen(data)
        d=parse.urlencode(d)
        d=d.encode('utf-8')
        res=self.tieba_fetch(url,self.BDUSS,d)
        return res

    def getCurrentInfo(self):
        '''获取实时的喜欢的贴吧及等级经验'''
        url='http://tieba.baidu.com/mo/q---B8D06B9EB00241F919F47789D4FD3103%3AFG%3D1--1-1-0--2--wapp_1385540291997_626/m?tn=bdFBW&tab=favorite'
        fetch_data=self.tieba_fetch(url,self.BDUSS)
        #print(fetch_data)
        data=self.tidyLikeData(fetch_data)
        #print(data)
        return data

    def genFidText(self):
        a=self.getCurrentInfo()
        likeNUM=len(a)
        data=[]
        #初始化
        for i in range(likeNUM):
            data.append({})
        for i in range(likeNUM):
            data[i]['kw']=a[i]['kw']
            data[i]['fid']=self.getfid(a[i]['kw'])
        with open('fid.txt','w',encoding='utf-8') as f:
            b=json.dumps(str(data))
            f.write(b)
            print('写如fid信息到文件成功！')

    def readFid(self):
        with open('fid.txt','r',encoding='utf-8') as f:
            a=f.read()
            b=json.loads(a)
            c=eval(b)
        return c

    def signAll(self):
        print('正在执行签到...')
        if path.exists('fid.txt'):
            sign_list=self.readFid()
        else:
            self.genFidText()
            sign_list=self.readFid()
        if sign_list:
            #print(sign_list)
            num=len(sign_list)
            fail=[]
            fail_d=[]
            success=[]
            success_d=[]
            for i in range(num):
                res=self.sign(sign_list[i]['kw'],sign_list[i]['fid'])
                print('正在签到【'+sign_list[i]['kw']+'】吧\t',end='')
                if res['error_code']=='0':
                    success.append(i)
                    print('\t√成功')
                elif res['error_code']=='160002':
                    success.append(i)
                    print('\t√之前已经签到过')
                else:
                    fail.append(i)
                    print('\t×失败')
        for i in range(len(success)):
            success_d.append(None)
        for i in range(len(success)):
            success_d[i]=sign_list[success[i]]
            #print('成功签到'+sign_list[success[i]]['kw']+'吧'+'\n')
        for i in range(len(fail)):
            fail_d.append(None)
        for i in range(len(fail)):
            fail_d[i]=sign_list[fail[i]]
            #print('签到失败'+sign_list[fail[i]]['kw']+'吧'+'\n')

        return {'success':success_d,'fail':fail_d}


