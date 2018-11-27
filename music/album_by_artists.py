# -*- coding:utf-8 -*-
"""
根据上一步获取的歌手的 ID 来用于获取所有的专辑 ID
"""

from bs4 import BeautifulSoup
import time
from music import sql
from urllib.parse import urlencode
from selenium import webdriver


class Album(object):


    # 浏览器处理
    def handle_brower(self, url):

        time.sleep(5)
        # 启动时 不用打开浏览器
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=option)
        driver.get(url)
        driver.switch_to_frame('g_iframe')
        soup = BeautifulSoup(driver.page_source, 'lxml')
        body = soup.body
        driver.close()
        return body

    # 处理专辑数据
    def handle_album(self, artist_id, limit, offset):
        params = {'id': artist_id, 'limit': limit, 'offset': offset}
        base_url = 'https://music.163.com/#/artist/album?'
        url = base_url + urlencode(params)
        body = self.handle_brower(url)
        # 获取页码数目
        a_list = body.find_all('a', attrs={'class': 'zpgi'})
        self.save_album(artist_id, limit, len(a_list))

    # 保存专辑
    def save_album(self, artist_id, limit, a_list):

        albums = []
        albums_name = []
        for i in range(0, int(a_list)):
            params = {'id': artist_id, 'limit': limit, 'offset': i*12}
            base_url = 'https://music.163.com/#/artist/album?'
            url = base_url + urlencode(params)
            body = self.handle_brower(url)

            album_name = body.find_all('a', attrs={'class': 'tit s-fc0'})
            album_id = body.find_all('a', attrs={'class': 'msk'})

            albums.extend(album_id)
            albums_name.extend(album_name)

        for i in range(0, len(albums)):
            try:
                album_name = albums_name[i].get_text()
                album_id = albums[i]['href'].replace('/album?id=', '').strip()

                sql.insert_album(artist_id, album_name, album_id)

            except Exception as e:
                raise e



if __name__ == "__main__":

    album = Album()
    album.handle_album('4941', '12', '0')



