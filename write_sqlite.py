#!/usr/bin/env python 3.7
# -*- coding: utf-8 -*-
# @Time       : 2019/8/14 14:12
# @Author     : wangxingxing
# @Email      : xingfengwxx@gmail.com 
# @File       : write_sqlite.py
# @Software   : PyCharm
# @Description: 写入json数据到sqllite

import json
import os
import sqlite3


def write_sqlite():
    if not os.path.exists('Girl.db'):
        conn = sqlite3.connect('Girl.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE PIC_INFO
        (ID INT PRIMARY KEY    NOT NULL,
        TITLE           TEXT   NOT NULL,
        TIMES           TEXT   NOT NULL,
        IMG_URL         TEXT   NOT NULL,
        PREVIEW         TEXT   NOT NULL,
        URLS            TEXT   NOT NULL);
        ''')
        print('Table created successfully')
        conn.commit()
        conn.close()
    # 读取json数据
    with open('back.json', 'r', encoding='utf-8') as f:
        # 数据有格式化
        dict_back = json.load(f)
    with open('test.json', 'r', encoding='utf-8') as f:
        # 图片更全，使用test文件即可(17年-18年)
        dict_test = json.load(f)
    with open('data.json', 'r', encoding='utf-8') as f:
        # 新的图片地址（18年-19年）
        dict_data = json.load(f)

    conn = sqlite3.connect('Girl.db')
    c = conn.cursor()
    # 首先删除表中所有数据
    c.execute('delete from PIC_INFO;')
    print('len_test=%d, len_data=%d, len_total=%d' %
          (len(dict_test), len(dict_data), len(dict_test) + len(dict_data)))
    # 自增ID,ID起始数等于前面字典元素个数之和
    num = 0
    write_file(conn, c, dict_test, num)
    write_file(conn, c, dict_data, len(dict_test))

    conn.close()
    print('写入数据库完成')


def write_file(conn, cursor, dict_data, num):
    for (key, value) in dict_data.items():
        num += 1
        # print('%s ---> %s' % (key, value))
        # 把urls数组组装成字符串，用;号分割
        str_urls = ''
        for u in value['urls']:
            str_urls += u
            str_urls += ';'
        sql = "INSERT INTO PIC_INFO VALUES(%d, '%s', '%s', '%s', '%s', '%s')" % \
              (num, key, value['times'], value['img_url'], value['preview'], str_urls)
        cursor.execute(sql)
        conn.commit()


if __name__ == '__main__':
    write_sqlite()