from tieba import Tieba

import time
BDUSS=''
a=Tieba(BDUSS)
list=a.readList()
def sign(kw,fid):
    r=a.sign(kw,fid)
    return r
def log(success,fail):
    now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    with open('log.txt','a',encoding='utf-8') as f:
        string='%s\t\t 成功：%s 失败:%s\n'% (now,success,fail)
        f.write(string)

round=1
success=0
fail=0
fail_list=[]
#list=list[:10]
while len(list)!=0:
    print('第',round,'轮签到：')
    for i in range(len(list)):
        str='正在签到 【%-12s】吧\t' % list[0][0]
        print(str,end='')
        r=sign(list[0][0],list[0][1])
        if r['error_code']=='0':
            print('成功！')
            list.pop(0)
            success+=1
        elif r['error_code']=='160002':
            print('已经签到过了')
            list.pop(0)
            success+=1
        else:
            print('失败了')
            #失败时将失败的贴吧置于列表尾部
            list.append(list.pop(0))
            fail+=1
    round+=1
    print('成功：',success,'失败：',fail)
log(success,fail)
