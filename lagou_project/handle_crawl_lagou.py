import json
import re
import time
import  multiprocessing #多进程
from lagou_project.handler_insert_data import lagou_mysql

import requests

# 代码地址：https://git.imooc.com/coding-363/Job_data_analysis
class HandleLaGou(object):
    def __init__(self):
        # 使用session保存cookies信息
        self.lagou_session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }
        self.city_list = ""

    # 获取全国所有城市列表的方法
    def handle_city(self):
        #该正则没写好，只能匹配到一部分
        # city_search = re.compile(r'zhaopin/">(.*?)</a>')
        city_search = re.compile(r'www\.lagou\.com\/.*\/">(.*?)</a>')
        city_url = "https://www.lagou.com/jobs/allCity.html"
        city_result = self.handle_request(method="GET", url=city_url)
        # print(city_result)
        # 使用正则表达式获取城市列表
        self.city_list = city_search.findall(city_result)
        # 手动清除里面的session信息
        self.lagou_session.cookies.clear()

    def handle_city_job(self, city):
        first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % city
        first_response = self.handle_request(method="GET", url=first_request_url)
        # print(first_response)
        total_page_search = re.compile(r'class="span\stotalNum">(\d+)</span>')
        try:
            total_page = total_page_search.search(first_response).group(1)
            # print(total_page)
        # 由于没有岗位信息造成的exception
        except:
            return
        else:
            for i in range(1,int(total_page)+1):
                data ={
                    "pn" : i,
                    "kd" : "python"
                }
                page_url = "https://www.lagou.com/jobs/positionAjax.json?px=default&city=%s&needAddtionalResult=false"%city
                referer_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput="%city
                # referer的url需要进行encode()
                self.header['Referer'] = referer_url.encode()
                response = self.handle_request(method="POST", url=page_url, data=data,info=city)
                # print(response)
                lagou_data = json.loads(response)#解析json数据
                job_list = lagou_data['content']['positionResult']['result']
                for job in job_list:
                    # print(job)
                    lagou_mysql.insert_item(job)

    def handle_request(self, method, url, data=None, info=None):
        while True:
            # 加入阿布云ip动态代理
            # proxyinfo = "http://..."
            # proxy ={
            #     "http": proxyinfo,
            #     "https": proxyinfo
            # }
            # 代理不稳定，需要try,并在请求的时候加上timeout
            if method == "GET":
                response = self.lagou_session.get(url=url, headers=self.header)
                # response = self.lagou_session.get(url=url, headers=self.header,proxies =proxy)
                response.encoding = 'utf-8'
            elif method == "POST":
                response = self.lagou_session.post(url=url, headers=self.header,data=data)
                # response = self.lagou_session.post(url=url, headers=self.header,data=data,proxies =proxy)
                response.encoding = 'utf-8'
            if '频繁' in response.text:
                print('频繁操作~~~')
                print(response.text)#打印当前ip地址
                # 需要先清除cookies信息
                self.lagou_session.cookies.clear()
                # 重新获取cookies信息
                first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" %info
                self.handle_request(method="GET", url=first_request_url)
                time.sleep(10)#休息10秒，模拟人的正常操作
                continue
                # print(first_response)
            return response.text


if __name__ == '__main__':
    lagou = HandleLaGou()
    # 获取所有城市
    lagou.handle_city()
    # 引入多进程加速抓取
    #创建进程池:此处创建了2个进程
    pool = multiprocessing.Pool(2)
    print(lagou.city_list)
    for city in lagou.city_list:
        print(city)
        # lagou.handle_city_job(city)
        pool.apply_async(lagou.handle_city_job,args=(city,)) #将数据提交到进程池中
    pool.close()
    pool.join()