# -*- coding: utf-8 -*-
import requests
import re
import time
import random
import sys
import datetime
from urllib.request import quote, unquote


class WenJuanXing:
    def __init__(self, id):
        """
        :param id:要填写的问卷的id
        """
        self.wj_url = 'https://ks.wjx.top/m/' + id + '.aspx'
        self.wj_id = id
        self.post_url = None
        self.header = None
        self.cookie = None
        self.data = None

    def set_data(self):
        """
        这个函数中生成问卷的结果，可根据问卷结果，随机生成答案
        :return:
        """
        # 改掉这里的数据
        self.data = {
            'submitdata': '1$红花会帮主}2$3}3$1|2}4$1}5$1}6$1^1}7$1}8$1'

        }

    def set_header(self):
        """
        随机生成ip，设置X-Forwarded-For
        ip需要控制ip段，不然生成的大部分是国外的
        :return:
        """
        ip = '{}.{}.{}.{}'.format(112, random.randint(
            64, 68), random.randint(0, 255), random.randint(0, 255))
        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': self.wj_url,
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.3; zh-cn; YL-Coolpad 5892_C00 Build/JLS36C) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
            'X-Forwarded-For': ip,
            'Cookie': 'jcn{}={}'.format(self.wj_id, quote(your_name, safe=";/?:@&=+$,", encoding="utf-8"))
            # 你的名字是用Cookie传上去的，如果没有这个Cookie，你就变成了匿名用户
        }

    def get_ktimes(self):
        """
        随机生成一个ktimes,ktimes是构造post_url需要的参数，为一个整数
        :return:
        """
        return random.randint(100, 200)

    def get_response(self):
        """
        访问问卷网页，获取网页代码
        :return: get请求返回的response
        """
        print("Try to f**k " + self.wj_url)
        response = requests.get(
            url=self.wj_url, headers=self.header, verify=False)
        self.cookie = response.cookies
        return response

    def get_jqnonce(self, response):
        """
        通过正则表达式找出jqnonce,jqnonce是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的jqnonce
        """
        jqnonce = re.search(r'.{8}-.{4}-.{4}-.{4}-.{12}', response.text)
        return jqnonce.group()

    def get_rn(self, response):
        """
        通过正则表达式找出rn,rn是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的rn
        """
        rn = re.search(r'\d{9,10}\.\d{8}', response.text)
        return rn.group()

    def get_id(self, response):
        """
        通过正则表达式找出问卷id,问卷是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的问卷id
        """
        id = re.search(r'\d{8}', response.text)
        return id.group()

    def get_jqsign(self, ktimes, jqnonce):
        """
        通过ktimes和jqnonce计算jqsign,jqsign是构造post_url需要的参数
        :param ktimes: ktimes
        :param jqnonce: jqnonce
        :return: 生成的jqsign
        """
        result = []
        b = ktimes % 10
        if b == 0:
            b = 1
        for char in list(jqnonce):
            f = ord(char) ^ b
            result.append(chr(f))
        return ''.join(result)

    def get_start_time(self, response):
        """
        通过正则表达式找出问卷starttime,问卷是构造post_url需要的参数
        :param response: 访问问卷网页，返回的reaponse
        :return: 找到的starttime
        """
        #start_time = re.search(r'\d+?/\d+?/\d+?\s\d+?:\d{2}', response.text) #原来获取到的开始时间是不带最后的秒数的
        
        start_time = re.search(r'\d+?/\d+?/\d+?\s\d+?:\d{2}:\d{2}', response.text) #这个是带最后的秒数的
        time.sleep(1) # 等待一小会再提交，减少出验证码的概率

        #用电脑本地时间获取starttime
        #因为部分人的电脑时间和标准的北京时间差的太大了，原本的2秒交卷变成了1分钟交卷，所以放弃了这段代码
        #a = datetime.datetime.now() + datetime.timedelta(seconds=-5) 
        #b = re.sub(r'\w+[^.]$', "", str(a))
        #c = re.sub(r'\.', "", b)
        #start_time = re.sub(r'\-', "/", c)

        return start_time.group()

    def set_post_url(self):
        """
        生成post_url
        :return:
        """
        self.set_header()  # 设置请求头，更换ip
        response = self.get_response()  # 访问问卷网页，获取response
        ktimes = self.get_ktimes()  # 获取ktimes
        jqnonce = self.get_jqnonce(response)  # 获取jqnonce
        rn = self.get_rn(response)  # 获取rn
        id = self.wj_id  # 获取问卷id
        jqsign = self.get_jqsign(ktimes, jqnonce)  # 生成jqsign
        start_time = self.get_start_time(response)  # 获取starttime
        #time_stamp = '{}{}'.format(int(time.time()), random.randint(100, 200)) # 生成一个时间戳，最后三位为随机数
        time_stamp = '{}{}'.format(int(time.time()), 000) #有资料说最后三位为毫秒，就干脆改为000了
        url = 'https://www.wjx.cn/joinnew/processjq.ashx?submittype=1&source=directphone&curID={}&t={}&starttim' \
              'e={}&ktimes={}&rn={}&hlv=1&jqnonce={}&jqsign={}'.format(
                  id, time_stamp, start_time, ktimes, rn, jqnonce, jqsign)
        self.post_url = url  # 设置url
        print(self.post_url)

    def post_data(self):
        """
        发送数据给服务器
        :return: 服务器返回的结果
        """
        self.set_data()
        print("F**king " + self.wj_id + " with " + self.data['submitdata'])
        response = requests.post(url=self.post_url, data=self.data,
                                 headers=self.header, cookies=self.cookie, verify=False)
        return response

    def run(self):
        """
        填写一次问卷
        :return:
        """
        self.set_post_url()
        print("Go Ahead!")
        result = self.post_data()
        print(result.text)
        return result.text

    def mul_run(self, n):
        """
        填写多次问卷
        :return:
        """
        for i in range(n):
            time.sleep(60)
            self.run()


if __name__ == '__main__':
    # 改成自己的问卷ID
    # http://www.wjx.top/m/{这就是ID}.aspx
    w = WenJuanXing("71431917")
    your_name = '红花会7帮主'
    while(w):
        r = w.run()
        if r.find("complete") >= 0:
            print("Yattaze!")
            break
        print("Oh s**t, submit failed. Let's try again later...")
        time.sleep(random.randint(5, 10))
