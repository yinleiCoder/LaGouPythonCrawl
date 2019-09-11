import time
from collections import Counter

from sqlalchemy import func

from lagou_project.create_lago_tables import Lagoutables
from lagou_project.create_lago_tables import Session


class HandleLagouData(object):
    def __init__(self):
        #实例化session信息
        self.mysql_session = Session()
        self.date = time.strftime("%Y-%m-%d", time.localtime())

    # 数据的存储方法
    def insert_item(self, item):
        #今天
        date = time.strftime("%Y-%m-%d", time.localtime())
        #存储的数据结构
        data = Lagoutables(
            # 岗位ID
            positionID=item['positionId'],
            # 经度
            longitude=item['longitude'],
            # 纬度
            latitude=item['latitude'],
            # 岗位名称
            positionName=item['positionName'],
            # 工作年限
            workYear=item['workYear'],
            # 学历
            education=item['education'],
            # 岗位性质
            jobNature=item['jobNature'],
            # 公司类型
            financeStage=item['financeStage'],
            # 公司规模
            companySize=item['companySize'],
            # 业务方向
            industryField=item['industryField'],
            # 所在城市
            city=item['city'],
            # 岗位标签
            positionAdvantage=item['positionAdvantage'],
            # 公司简称
            companyShortName=item['companyShortName'],
            # 公司全称
            companyFullName=item['companyFullName'],
            # 公司所在区
            district=item['district'],
            # 公司福利标签
            companyLabelList=','.join(item['companyLabelList']),
            salary=item['salary'],
            # 抓取日期
            crawl_date=date
        )

        query_result = self.mysql_session.query(Lagoutables).filter(Lagoutables.crawl_date == date,
                                                                    Lagoutables.positionID == item[
                                                                        'positionId']).first()
        #判断该条岗位信息是否存在
        if query_result:
            print('该岗位信息已经存在%s:%s:%s' % (item['positionId'], item['city'], item['positionName']))
        else:
            # 插入数据
            self.mysql_session.add(data)
            # 提交数据到数据库
            self.mysql_session.commit()
            print('新增岗位信息：%s' % item['positionId'])

        # 行业信息
    def query_industryfield_result(self):
        info = {}
        # 查询今日抓取到的行业信息数据
        result = self.mysql_session.query(Lagoutables.industryField).filter(
            Lagoutables.crawl_date == self.date
        ).all()
        result_list1 = [x[0].split(',')[0] for x in result]
        result_list2 = [x for x in Counter(result_list1).items() if x[1] > 150]
        # 填充的是series里面的data
        data = [{"name": x[0], "value": x[1]} for x in result_list2]
        name_list = [name['name'] for name in data]
        info['x_name'] = name_list
        info['data'] = data
        return info

        # 查询薪资情况
    def query_salary_result(self):
        info = {}
        # 查询今日抓取到的薪资数据
        result = self.mysql_session.query(Lagoutables.salary).filter(Lagoutables.crawl_date == self.date).all()
        # 处理原始数据
        result_list1 = [x[0] for x in result]
        # 计数,并返回
        result_list2 = [x for x in Counter(result_list1).items() if x[1] > 100]
        result = [{"name": x[0], "value": x[1]} for x in result_list2]
        name_list = [name['name'] for name in result]
        info['x_name'] = name_list
        info['data'] = result
        return info

    # 查询工作年限情况
    def query_workyear_result(self):
        info = {}
        # 查询今日抓取到的薪资数据
        result = self.mysql_session.query(Lagoutables.workYear).filter(Lagoutables.crawl_date == self.date).all()
        # 处理原始数据
        result_list1 = [x[0] for x in result]
        # 计数,并返回
        result_list2 = [x for x in Counter(result_list1).items()]
        result = [{"name": x[0], "value": x[1]} for x in result_list2 if x[1] > 15]
        name_list = [name['name'] for name in result]
        info['x_name'] = name_list
        info['data'] = result
        return info

    # 查询学历信息
    def query_education_result(self):
        info = {}
        # 查询今日抓取到的薪资数据
        result = self.mysql_session.query(Lagoutables.education).filter(Lagoutables.crawl_date == self.date).all()
        # 处理原始数据
        result_list1 = [x[0] for x in result]
        # 计数,并返回
        result_list2 = [x for x in Counter(result_list1).items()]
        result = [{"name": x[0], "value": x[1]} for x in result_list2]
        name_list = [name['name'] for name in result]
        info['x_name'] = name_list
        info['data'] = result
        return info

    # 岗位发布数量,折线图
    def query_job_result(self):
        info = {}
        result = self.mysql_session.query(Lagoutables.crawl_date, func.count('*').label('c')).group_by(
        Lagoutables.crawl_date).all()
        result1 = [{"name": x[0], "value": x[1]} for x in result]
        name_list = [name['name'] for name in result1]
        info['x_name'] = name_list
        info['data'] = result1
        return info

    # 根据城市计数
    def query_city_result(self):
        info = {}
        # 查询今日抓取到的薪资数据
        result = self.mysql_session.query(Lagoutables.city, func.count('*').label('c')).filter(
        Lagoutables.crawl_date == self.date).group_by(Lagoutables.city).all()
        result1 = [{"name": x[0], "value": x[1]} for x in result]
        name_list = [name['name'] for name in result1]
        info['x_name'] = name_list
        info['data'] = result1
        return info

    # 融资情况
    def query_financestage_result(self):
        info = {}
        # 查询今日抓取到的薪资数据
        result = self.mysql_session.query(Lagoutables.financeStage).filter(
        Lagoutables.crawl_date == self.date).all()
        # 处理原始数据
        result_list1 = [x[0] for x in result]
        # 计数,并返回
        result_list2 = [x for x in Counter(result_list1).items()]
        result = [{"name": x[0], "value": x[1]} for x in result_list2]
        name_list = [name['name'] for name in result]
        info['x_name'] = name_list
        info['data'] = result
        return info

    # 公司规模
    def query_companysize_result(self):
        info = {}
        # 查询今日抓取到的薪资数据
        result = self.mysql_session.query(Lagoutables.companySize).filter(Lagoutables.crawl_date == self.date).all()
        # 处理原始数据
        result_list1 = [x[0] for x in result]
        # 计数,并返回
        result_list2 = [x for x in Counter(result_list1).items()]
        result = [{"name": x[0], "value": x[1]} for x in result_list2]
        name_list = [name['name'] for name in result]
        info['x_name'] = name_list
        info['data'] = result
        return info

    # 任职情况
    def query_jobNature_result(self):
        info = {}
        # 查询今日抓取到的薪资数据
        result = self.mysql_session.query(Lagoutables.jobNature).filter(Lagoutables.crawl_date == self.date).all()
        # 处理原始数据
        result_list1 = [x[0] for x in result]
        # 计数,并返回
        result_list2 = [x for x in Counter(result_list1).items()]
        result = [{"name": x[0], "value": x[1]} for x in result_list2]
        name_list = [name['name'] for name in result]
        info['x_name'] = name_list
        info['data'] = result
        return info

    # 抓取数量
    def count_result(self):
        info = {}
        info['all_count'] = self.mysql_session.query(Lagoutables).count()
        info['today_count'] = self.mysql_session.query(Lagoutables).filter(
        Lagoutables.crawl_date == self.date).count()
        return info

        # def query_city_salary_industryfidle(self):
        #     result = self.mysql_session.query(func.lower(func.substring_index(Lagoutables.industryField,',',1)),
        #                                       Lagoutables.city,
        #                                       func.avg(func.replace(func.lower(func.substring_index(Lagoutables.salary,'-',2)),'k','')),
        #                                       func.count(func.lower(func.substring_index(Lagoutables.industryField,',',1))).label('c')).filter(
        #         Lagoutables.crawl_date == self.date
        #     ).group_by(func.lower(func.substring_index(Lagoutables.industryField,',',1)),
        #                Lagoutables.city).all()
        #     result_list = [{"industry":item[0],"city":item[1],"salary_avg":int(item[2]),"value":item[3]} for item in result if item[3] >10]
        #     info = {}
        #     # city_list = set([city[1] for city in result])
        #     city_list = set([city['city'] for city in result_list])
        #     # industryfield_list = set([industry[0] for industry in result])
        #     industryfield_list = set([x['industry'] for x in result_list])
        #     series_list = []
        #     for city in city_list:
        #         series_item = {}
        #         series_data_list = []
        #         series_item['name'] = city
        #         series_item['type'] = "bar"
        #         for item in industryfield_list:
        #             series_data_item = {}
        #             series_data_item['name'] = item
        #             value = [x['salary_avg'] for x in result_list if x['industry'] == item and x['city'] == city]
        #             if value:
        #                 series_data_item['value'] = value[0]
        #                 series_data_list.append(series_data_item)
        #         series_item['data'] = series_data_list
        #         series_list.append(series_item)
        #     info['x_name'] = list(industryfield_list)
        #     info['legend_data'] = list(city_list)
        #     info['data'] = series_list
        #     return info


lagou_mysql = HandleLagouData()