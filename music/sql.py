# -*- coding:utf-8 -*-

import pymysql.cursors

# 数据库配置
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'zhou_123',
    'database': 'music',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.Cursor
}

# 连接数据库
connection = pymysql.Connect(**config)


# 保存歌手
def insert_artist(artist_id, artist_name):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `artists` (`ARTIST_ID`, `ARTIST_NAME`) VALUES (%s, %s)"
        cursor.execute(sql, (artist_id, artist_name))
    connection.commit()


# 保存专辑
def insert_album(artist_id, album_name, album_id):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `albums` (`artist_id`, `album_id`, `album_name`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (artist_id, album_id, album_name))
    connection.commit()


# 保存音乐
def save_music(music_id, music_name, album_id):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `musics` (`music_id`, `music_name`, `album_id`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (music_id, music_name, album_id))
    connection.commit()

# 保存评论
def save_comments(c_name, c_content, c_time, c_votes, c_r_name, c_r_content):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `comments`(`c_name`, `c_content`, `c_time`, `c_votes`, `c_r_name`, `c_r_content`) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (c_name, c_content, c_time, c_votes, c_r_name, c_r_content))
    connection.commit()







