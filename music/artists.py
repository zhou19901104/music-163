# -*- coding:utf-8 -*-
"""
获取所有歌手的信息
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlencode
from music import sql
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


class Artists(object):

    def __init__(self, url):
        self.url = url
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')


    def driver_init(self, group_id, initial):
        """
        :param group_id: 
        :param initial: 
        :return: 
        """
        params = {'id': group_id, 'initial': initial}
        # 解析url
        url = self.url + urlencode(params)
        driver = webdriver.Chrome()
        # driver = webdriver.Chrome(chrome_options=self.chrome_options)
        driver.get(url)
        # 选择iframe框架
        driver.switch_to.frame('g_iframe')
        return driver


    def artist_info(self, driver):
        """
        保存歌手的信息
        :return: 
        """
        time.sleep(0.5)
        wait = WebDriverWait(driver, 10)
        # 判断确定页面加载完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'z-slt')))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        # iframe 的body体
        body = soup.body
        return body


    def save_artist(self, html):
        # 热门歌手
        hot_artists = html.find_all('a', attrs={'class': 'msk'})
        # 所有歌手
        artists = html.find_all('a', attrs={'class': 'nm nm-icn f-thide s-fc0'})

        for artist in hot_artists:
            artist_id = artist['href'].replace('/artist?id=', '').strip()
            artist_name = artist['title'].replace('的音乐', '').strip()
            # 插入数据库中
            try:
                sql.insert_artist(artist_id, artist_name)
            except Exception as e:
                print(e)

        for artist in artists:

            artist_id = artist['href'].replace('/artist?id=', '').strip()
            artist_name = artist.get_text()
            # 插入数据库
            try:
                sql.insert_artist(artist_id, artist_name)
            except Exception as e:
                print(e)

    def execute_save(self, group_id, start, end):
        """
        执行保存
        :param group_id: 
        :param initial: 
        :return: 
        """

        for i in range(start, end):
            driver = self.driver_init(group_id, i)
            html = self.artist_info(driver)
            try:
                self.save_artist(html)
            except Exception as e:
                print(e)
            time.sleep(1)


if __name__ == '__main__':

    url = 'https://music.163.com/#/discover/artist/cat?'
    artist = Artists(url)
    artist.execute_save(1001, 65, 70)








