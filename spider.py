import requests
from requests.exceptions import RequestException
import re
from lxml import etree
import chardet
import csv

import pymysql

db = pymysql.connect(host="8.133.167.76", user="root", passwd="1234", db="book_share_db", charset='UTF8' )
cursor = db.cursor()

def get_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = chardet.detect(response.content).get('encoding')
            html = response.text
            return html
    except RequestException:
        return None







def main():
    items = []
    for page in range(1, 2):
        url = 'https://search.51job.com/list/000000,000000,0000,32,9,99,%25E5%25A4%25A7%25E6%2595%25B0%25E6%258D%25AE%25E5%25BC%2580%25E5%258F%2591%25E5%25B7%25A5%25E7%25A8%258B%25E5%25B8%2588,2,' + '{}.html'.format(page)
        print("正在爬取第{}页".format(page))
        html = get_html(url)
        url_lists = re.findall('<script type="text/javascript">.*?engine_search_result":(.*),.*?"jobid_count"', html, re.S)
        url_lists = url_lists[0]
        url_lists = eval(url_lists)
        for url in url_lists:
            url = url.get('job_href')
            url = re.sub(r'\\', '', url)
            html = get_html(url)
            item = parse_html(html)
            items.append(item)
    # 保存到csv中
    save_csv(items)

def parse_html(html):
    try:
        # 返回xpath对象
        html_xpath = etree.HTML(html)
        # 职位名称
        job_title = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/h1/text()")
        job_title = job_title[0]
        # print("job_title:{}".format(job_title))
        # 公司名称
        company_name = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/p[@class='cname']/a/@title")
        company_name = company_name[0]
        print("company_name:{}".format(company_name))
        # 工作地点
        info = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/p[contains(@class, 'msg')]/@title")
        info = re.sub('[(xa0)(|)]', '', info[0])
        info = info.split()
        work_place = info[0]
        print("work_place:{}".format(work_place))
        # 工作经
        work_year = info[1]
        # print("work_year:{}".format(work_year))
        # 学历
        education = info[2]
        # print("education:{}".format(education))
        # 招聘人数
        recruit_number = info[3]
        # print("recruit_number:{}".format(recruit_number))
        # 发布时间
        release_time = info[4]
        # print("release_time:{}".format(release_time))
        # 公司性质
        company_nature = html_xpath.xpath("//div[@class='tCompany_sidebar']//div[@class='com_tag']/p[1]/@title")
        company_nature = company_nature[0]
        # print("company_nature:{}".format(company_nature))
        # 公司规模
        company_size = html_xpath.xpath("//div[@class='tCompany_sidebar']//div[@class='com_tag']/p[2]/@title")
        company_size = company_size[0]
        # print("company_size:{}".format(company_size))
        # 所属行业
        industry = html_xpath.xpath("//div[@class='tCompany_sidebar']//div[@class='com_tag']/p[3]/@title")
        industry = industry[0]
        # print("industry:{}".format(industry))
        # 工资
        salary = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/strong/text()")
        salary = salary[0]
        # print("salary:{}".format(salary))




        item = [job_title, company_name, work_place, work_year, education, recruit_number, release_time,
                company_nature, company_size, industry, salary]
        return item
    except:
        pass


def save_csv(items):
    for i in items:
        if i != None:
            job_title=  i[0]
            company_name = i[1]
            work_place = i[2]
            work_year = i[3]
            education = i[4]
            recruit_number = i[5]
            release_time = i[6]
            company_nature = i[7]
            company_size = i[8]
            industry = i[9]
            salary = i[10]
            print(job_title, company_name, work_place, work_place, education, recruit_number, release_time,  company_nature, company_size, industry, salary)

            sql = """insert into book_share_db.wether_test(job_title, company_name, work_place, work_year, education, recruit_number, release_time,  company_nature, company_size, industry, salary)   values( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (job_title, company_name, work_place, work_year, education, recruit_number, release_time, company_nature, company_size, industry, salary))
            db.commit()
            print(sql)
    # with open("招聘信息.csv", 'w', newline='', encoding='utf-8') as csvfile:
    #     csv_tags = ['职位名称', '公司名称', '工作地点', '工作经验', '学历', '招聘人数', '发布时间', '公司性质', '公司规模',
    #                   '所属行业', '工资']
    #     writer = csv.writer(csvfile)
    #     writer.writerow(csv_tags)
    #     for item in items:
    #         if item != None:
    #             writer.writerow(item)


if __name__ == '__main__':
    main()