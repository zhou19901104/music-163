# -*- coding:utf-8 -*-
"""
根据专辑爬去所有的歌曲信息
"""

from selenium import webdriver
from urllib.parse import urlencode
from music import sql
from bs4 import BeautifulSoup
import re


class Music(object):


    # 保存音乐
    def save_music(self, album_id):

        params = {'id': album_id}
        # 启动时 不用打开浏览器
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=option)

        base_url = 'https://music.163.com/#/album?'
        url = base_url + urlencode(params)

        driver.get(url)
        driver.switch_to_frame('g_iframe')

        soup = BeautifulSoup(driver.page_source, 'lxml')
        body = soup.body


        musics_id = body.select('span[class="txt"] > a')
        musics_name = body.select('div[class="ttc"] > span > a > b')

        for i in range(0, len(musics_id)):

            # 正则匹配
            pattern = re.compile(r'<b title="(.*)">(.*)<div(.*)<\/div>(.*)<\/b>')
            music = re.search(pattern, str(musics_name[i]))
            # 获取歌曲名称
            music_name = music.group(1)
            music_id = musics_id[i]['href'].replace('/song?id=', '').strip()
            sql.save_music(music_id, music_name, album_id)


        driver.close()


if __name__ == '__main__':

    music = Music()
    music.save_music('2263029')
