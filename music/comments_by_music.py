# -*- coding:utf-8 -*-
"""
根据音乐爬取评论数
"""

import time, datetime
import re
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pandas import DataFrame
from music import sql


class Comments(object):


    def __init__(self, id):
        self.id = id
        self.url = 'https://music.163.com/#/song?id=%s' % self.id
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.people = {'names': [], 'comments': [], 'dates': [], 'votes': [], 'replied_names': [], 'replied_comments': []}


    def search(self):
        """根据歌曲名称来搜索歌曲"""
        driver = webdriver.Chrome()

        # 无窗口模式的浏览器
        # driver = webdriver.Chrome(chrome_options=self.chrome_options)
        driver.get(self.url)
        time.sleep(0.5)

        # 无窗口模式下，放大窗口，找到input 输入框,并输入name,按下ENTER键
        # driver.set_window_size(1200, 800)
        # put = driver.find_element_by_id("srch")
        # put.send_keys(self.name)
        # time.sleep(0.5)
        # put.send_keys(Keys.ENTER)
        # time.sleep(0.5)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'g_iframe')))
        driver.switch_to_frame('g_iframe')
        time.sleep(1)

        # # 选中单曲列表
        # put = driver.find_element_by_class_name('z-slt')
        # put.click()

        # # 显示等待
        # wait = WebDriverWait(driver, 10)
        # # 两个条件验证元素是否出现，传入的参数都是元组类型的locator，如(By.ID, ‘kw’)
        # wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'w0')))

        return driver


    def download_next_page(self, driver):
        """
        获取本页的html代码并且跳转到下一页
        :param page: 
        :return: 本页面的html代码
        """
        time.sleep(0.5)
        wait = WebDriverWait(driver, 10)
        # 判断确定页面加载完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME,'itm')))
        content = driver.page_source
        # 输出时按照网页上的格式换行保存评论内容
        content = content.replace('<br />','\n')
        html = BeautifulSoup(content, 'lxml')

        # 获取下一页的按钮
        next_page = driver.find_element_by_class_name('znxt')
        time.sleep(0.5)
        # 滚动条滚动到底部
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # 点击下一页
        next_page.click()

        return html

    def download_previous_page(self, driver):
        """
        获取上一页的HTML代码
        :param driver: 
        :return: 
        """
        time.sleep(1)
        previous_page = driver.find_element_by_class_name('zprv')
        previous_page.click()
        # 因为向前翻页的时候页面都已经加载过了所以不需要再把滚动条拉下来
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'itm')))
        content = driver.page_source
        content = content.replace('<br />', '\n')
        html = BeautifulSoup(content, 'lxml')
        return html

    def change_time(self, time):
        """
        把时间格式统一为%Y-%m-%d %H:%M,但是时间过早的评论只显示了日期
        :param time: 
        :return: 
        """
        now = datetime.datetime.now()
        day = now.strftime('%Y-%m-%d')
        year = now.strftime('%Y')

        # 昨天
        yesterday = now + datetime.timedelta(days=-1)
        yesterday = yesterday.strftime('%Y-%m-%d')

        if '昨天' in time:
            time = time.replace('昨天', yesterday+ ' ')
        elif '前' in time:
            minut = int(time[:time.index('分')])
            time = (now + datetime.timedelta(minutes=-minut)).strftime('%Y-%m-%d %H:%M')
        elif len(time) == 5:
            time = day + ' ' + time
        elif time.index('月') == 1:
            time = time.replace('月', '-').replace('日', '')
            time = year + '-' + time
        elif '年' in time:
            time = time.replace('年', '-').replace('月', '-').replace('日', '')
        else:
            # print('不明时间格式')
            return None
        return time


    def change_vote(self, vote):
        """
        统一点赞数格式为int
        :param vote: 
        :return: 
        """
        try:
            # 删除非数字的字符串
            pattern = r'\D'
            if '万' in vote:
                change = re.sub(pattern, '', vote)
                change = int(change) * 10000
            else:
                change = int(re.sub(pattern, '', vote))
        except:
            change = 0
        return change


    def one_page_comments_download(self, html):
        """
        收集用户评论的内容，时间，姓名，点赞，针对谁的回复
        :param html: 
        :return: 
        """

        persons = html.find_all('div', attrs={'class': 'itm'})

        for person in persons:

            # 提取出评论内容，把姓名和内容分离
            comments = person.find(class_='cnt').text
            name = comments[:comments.index('：')]
            comment = comments[comments.index('：')+1:]
            date = person.find(class_='time')

            date = self.change_time(date.text)

            vote = person.select('div[class="rp"] > a')[0].text
            vote = self.change_vote(vote)

            # 评论和被评论的内容和姓名
            try:
                replied_comments = person.find(class_='que').text
                # 该评论已删除的情况
                if "删除" in replied_comments:
                    replied_comment = replied_comments
                    replied_name = None
                else:
                    replied_name = replied_comments[2:replied_comments.index('：')]
                    replied_comment = replied_comments[replied_comments.index('：')+1:]
            except AttributeError as e:
                replied_comment = None
                replied_name = None

            self.people['names'].append(name)
            self.people['comments'].append(comment)
            self.people['dates'].append(date)
            self.people['votes'].append(vote)
            self.people['replied_names'].append(replied_name)
            self.people['replied_comments'].append(replied_comment)

        return self.people

    def save_mysql(self, people):

        for i in range(len(people['names'])):
            sql.save_comments(people['names'][i],people['comments'][i],people['dates'][i],people['votes'][i],people['replied_names'][i],people['replied_comments'][i])



    def save_csv(self, people):
        """
        把数据存储进csv文件
        :param people: 
        :return: 
        """
        people = DataFrame(people)
        people.to_csv(os.getcwd()+'/comments.csv', encoding='utf_8_sig')
        # 因为根据评论制作词云，所以单独再输出下面的txt文件
        people.to_csv(os.getcwd()+'/use.txt', columns=['comments'], index=0, header=0)

    def collent_comments(self, n=1, style=[]):
        """
        爬取储存
        :param n: 爬取的页数  
        :param id:  爬取歌曲的id
        :param style: 以什么方式存储
        :return: 
        """
        driver = self.search()
        html = []
        if n < 1:
            print('输入有误')
            driver.close()
            return
        elif n>=1:
            try:

                for i in range(int(n)):
                    # html 追加下一页的代码
                    html.append(self.download_next_page(driver))
                    # 提取数据
                    self.one_page_comments_download(html[i])
                    time.sleep(1)
            except Exception as e:
                print(e)
            finally:
                driver.close()
                return self.people


if __name__ == '__main__':

    id = '454924421'
    comment = Comments(id)
    people = comment.collent_comments(9, style=[])
    comment.save_csv(people)








