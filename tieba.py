import hashlib
import json
import sys
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from urllib import parse

import requests
from requests_html import HTML


class Tieba:
    def __init__(self, BDUSS):
        self.BDUSS = BDUSS
        self.headers = {"Cookie": "BDUSS=" + self.BDUSS}
        self.fav_json_path = Path.cwd().joinpath("tieba.json")
        self.fav = self.load_fav_from_local()

    def get_html(self, url):
        r = requests.get(url, headers=self.headers, timeout=8)
        if r.ok:
            return r.text
        return None

    def get_json(self, url):
        r = requests.get(url, headers=self.headers, timeout=8)
        if r.ok:
            return r.json()
        return None

    def post(self, url, data):
        r = requests.post(url, headers=self.headers, data=data, timeout=8)
        if r.ok:
            return r.json()
        return {}

    def encodeData(self, data):
        """主要是计算sign的值"""
        SIGN_KEY = "tiebaclient!!!"
        s = ""
        keys = data.keys()
        for i in sorted(keys):
            # s += i + "=" + str(data[i])
            s += f"{i}={data[i]}"
        sign = hashlib.md5((s + SIGN_KEY).encode("utf-8")).hexdigest().upper()
        data.update({"sign": str(sign)})
        return data

    # 签到基本函数
    def _sign(self, tiebainfo):
        url = "http://c.tieba.baidu.com/c/c/forum/sign"
        kw = tiebainfo.get("title")
        data = {
            "BDUSS": self.BDUSS,
            "fid": tiebainfo.get("fid"),
            "kw": kw,
            "tbs": self.get_tbs(),
        }
        d = self.encodeData(data)
        d = parse.urlencode(d)
        d = d.encode("utf-8")
        res = self.post(url, d)
        if res["error_code"] == "0":
            msg = "√"
        elif res["error_code"] == "160002":
            msg = "已经签到过了"
        else:
            msg = "×"
        print(f"签到 {kw:<14}吧   {msg}")
        return res

    def sign(self):
        print(f"共需签到{len(self.fav)}个贴吧")
        pool = ThreadPool(4)
        pool.map(self._sign, self.fav)
        pool.close()
        pool.join()
        print("签到完成")

    def get_fid(self, kw):
        """
        获取某个贴吧的fid
        {'no': 0, 'error': '', 'data': {'fid': 1878539, 'can_send_pics': 1}}
        """
        fid_url = f"http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname={parse.quote(kw)}"
        data = self.get_json(fid_url)
        return data["data"]["fid"]

    def get_tbs(self):
        """
        获取tbs值 {'tbs': '73f11340bfef6f2c1619647285', 'is_login': 1}
        这里可以判断是否登录
        """
        url = "http://tieba.baidu.com/dc/common/tbs"
        r = self.get_json(url)
        if r:
            return r["tbs"]
        return None

    def _get_fav_info(self, dom):
        """从HTML中提取贴吧名称、等级、经验信息"""
        title = dom.find("td a")[0].text
        level = dom.find("td")[1].text.split("等级")[1]
        exp = dom.find("td")[2].text.split("经验值")[1]
        return {"title": title, "level": level, "exp": exp}

    def get_fav(self):
        """获取关注的贴吧列表"""
        fav_url = "http://tieba.baidu.com/mo/q---B8D06B9EB00241F919F47789D4FD3103%3AFG%3D1--1-1-0--2--wapp_1385540291997_626/m?tn=bdFBW&tab=favorite"
        raw_html = self.get_html(fav_url)
        if raw_html:
            html = HTML(html=raw_html)
            fav_dom = html.find("div.d tr")
            fav_list = list(map(self._get_fav_info, fav_dom))
            # 获取 fid
            fav_len = len(fav_list)
            for index, fav_data in enumerate(fav_list):
                sys.stdout.write(f" 收集数据: {int(index * 100 / fav_len)}\r")
                sys.stdout.flush()
                fav_data["fid"] = self.get_fid(fav_data["title"])
            return fav_list
        return None

    def save_fav_to_local(self, fav):
        # 保存贴吧信息至本地
        with open(self.fav_json_path, "w", encoding="utf-8") as f:
            json.dump(fav, f, indent=2, ensure_ascii=False)
            print("保存成功！")

    def load_fav_from_local(self):
        if self.fav_json_path.exists():
            with open(self.fav_json_path, "r", encoding="utf-8") as f:
                fav = json.load(f)
        else:
            print("贴吧信息不存在")
            fav = self.get_fav()
            self.save_fav_to_local(fav)
        return fav


if __name__ == "__main__":
    bduss_path = Path.cwd().joinpath("BDUSS.txt")
    if bduss_path.exists():
        with open(bduss_path, "r", encoding="utf-8") as bduss_file:
            bduss = bduss_file.read().strip()
    else:
        bduss = input("请输入贴吧BDUSS: ")
        with open(bduss_path, "w", encoding="utf-8") as bduss_file:
            bduss_file.write(bduss)
    t = Tieba(bduss)
    t.sign()
