#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random
from os import path

import requests
from requests.adapters import HTTPAdapter

from bs4 import BeautifulSoup as bs
import uuid
import os
import time
from multiprocessing import Process

headers = dict()
headers[
    "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
headers["Accept-Encoding"] = "gzip, deflate, sdch"
headers["Accept-Language"] = "zh-CN,zh;q=0.8"
headers["Accept-Language"] = "zh-CN,zh;q=0.8"
request_retry = HTTPAdapter(max_retries=3)


def my_get(url, refer=None):
    session = requests.session()
    session.headers = headers
    if refer:
        headers["Referer"] = refer
    session.mount('https://', request_retry)
    session.mount('http://', request_retry)
    return session.get(url)


def get_type_content(url, mm_type):
    soup = bs(my_get(url).content, "lxml")
    # total_page = int(soup.select_one("a.next.page-numbers").find_previous_sibling().text) 已失效
    page_nums = soup.select(".page-numbers")
    total_page = int(page_nums[len(page_nums) - 2].text)
    print(f'共{total_page}页')
    for page in range(1, total_page + 1):
        get_page_content_api(page, mm_type)


def main():
    # types = ['xinggan', 'japan', 'taiwan', 'mm']
    types = ['xinggan', ]
    tasks = [Process(target=get_type_content, args=('https://www.mzitu.com/' + x, x,)) for x in types]
    for task in tasks:
        task.start()


def get_page_content(page, mm_type):
    href = "https://www.mzitu.com/" + mm_type + "/page/" + str(page)
    soup = bs(my_get(href).content, "lxml")
    li_list = soup.select("div.postlist ul#pins li")
    for li in li_list:
        get_pic(li.select_one("a").attrs["href"], mm_type)


def get_page_content_api(page, mm_type):
    href = "https://www.mzitu.com/" + mm_type + "/page/" + str(page)
    soup = bs(my_get(href).content, "lxml")
    li_list = soup.select("div.postlist ul#pins li")
    for li in li_list:
        # get_pic(li.select_one("a").attrs["href"], mm_type)
        get_pic_api(li, mm_type)


def get_pic_api(li, mm_type):
    print(li)
    img_info = li.find('img')
    # 获取标题
    title = img_info.attrs['alt']
    # 获取第一个a标签的href属性，网页地址
    img_url = li.select_one('a').attrs['href']
    # 获取封面预览地址
    preview = img_info.attrs['data-original']
    # 获取组图时间
    times = li.select_one('.time').text
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print('%s title=%s, img_url=%s, preview=%s, time=%s' % (local_time, title, img_url, preview, times))
    # 图片列表集合
    get_pic_urls_api(img_url, mm_type, title, preview, times)
    random_sleep()


def get_pic_urls_api(url, mm_type, title, preview, times):
    """
    :param url: 网页地址
    :return: 图片url列表
    """
    urls = []
    refer = url
    response = my_get(url)
    i = 0
    while "400" in bs(response.content, "lxml").title or response.status_code == 404 or response.status_code == 400:
        i += 1
        if i > 5:
            return
        random_sleep()
        response = my_get(url)
    li_soup = bs(response.content, "lxml")
    if li_soup.find(lambda tag: tag.name == 'a' and '下一页»' in tag.text) is None:
        with open("log.txt", "a") as fs:
            fs.write(url + "\r\n")
            fs.write(str(response.status_code) + "\r\n")
            fs.write(response.content + "\r\n")
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"{t}error:", url)
    else:
        total_page = int(li_soup.find(lambda tag: tag.name == 'a' and '下一页»' in tag.text) \
                         .find_previous_sibling().text)
        for page in range(1, total_page + 1):
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print('%s url=%s, title=%s, mm_type=%s' % (t, url + '/' + str(page), title, mm_type))
            # 需要下载图片打开这行
            # download_pic(url + "/" + str(page), title, mm_type, refer)
            # download_pic_api(url + '/' + str(page), refer)
            if page == 1:
                response = my_get(url, refer)
            else:
                response = my_get(url + '/' + str(page), refer)
            # href = bs(response.content, "lxml").select_one("div.main-image").attrs["src"]
            href = bs(response.content, "lxml").select_one("div.main-image p a img").attrs['src']
            urls.append(href)
            random_sleep()
        print('urls=', urls)
        # 构建字典
        dict_data = {'title': title, 'times': times, 'img_url': url, 'preview': preview, 'urls': urls}
        dict_total = {title: dict_data}
        print('dict_data: ', dict_total)
        # 保存为json文件
        save_json(dict_total)


def save_json(data):
    try:
        if not path.exists('data.json'):
            with open('data.json', 'w', encoding='utf-8') as f:
                dict_empty = {}
                json.dump(dict_empty, f, ensure_ascii=False, indent=4)
        with open('data.json', 'r', encoding='utf-8') as fo:
            # 先读取已存数据
            dict_old = json.load(fo)
            print('dict_old: ', dict_old)
        with open('data.json', 'w', encoding='utf-8') as fn:
            dict_new = {}
            dict_new.update(data)
            dict_new.update(dict_old)
            print('dict_new: ', dict_new)
            json.dump(dict_new, fn, ensure_ascii=False, indent=4)
    except IOError as e:
        print(e)


def download_pic_api(url, refer):
    response = my_get(url, refer)
    href = bs(response.content, "lxml").select_one("div.main-image img").attrs["src"]
    print('urls=', href)


def get_pic(url, mm_type):
    refer = url
    response = my_get(url)
    i = 0
    while "400" in bs(response.content, "lxml").title or response.status_code == 404 or response.status_code == 400:
        i += 1
        if i > 5:
            return
        random_sleep()
        response = my_get(url)
    li_soup = bs(response.content, "lxml")
    title = li_soup.title.text.replace(' ', '-')
    if li_soup.find(lambda tag: tag.name == 'a' and '下一页»' in tag.text) is None:
        with open("log.txt", "a") as fs:
            fs.write(url + "\r\n")
            fs.write(str(response.status_code) + "\r\n")
            fs.write(response.content + "\r\n")
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"{t}error:", url)
    else:
        total_page = int(li_soup.find(lambda tag: tag.name == 'a' and '下一页»' in tag.text) \
                         .find_previous_sibling().text)
        for page in range(1, total_page + 1):
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print('%s url=%s, title=%s, mm_type=%s' % (t, url + '/' + str(page), title, mm_type))
            # 需要下载图片打开这行
            # download_pic(url + "/" + str(page), title, mm_type, refer)
            random_sleep()


def download_pic(url, title, mm_type, refer):
    response = my_get(url, refer)
    href = bs(response.content, "lxml").select_one("div.main-image img").attrs["src"]
    response = my_get(href)
    i = 0
    while response.status_code != 200:
        i += 1
        if i > 5:
            return
        random_sleep()
        response = my_get(url)

    if not os.path.exists("img"):
        os.mkdir("img")
    if not os.path.exists("img/" + mm_type):
        os.mkdir("img/" + mm_type)
    if not os.path.exists("img/" + mm_type + "/" + title):
        os.mkdir("img/" + mm_type + "/" + title)
    with open("img/" + mm_type + "/" + title + "/" + str(uuid.uuid1()) + ".jpg", 'wb') as fs:
        fs.write(response.content)
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"{t} download success:", title)


def random_sleep():
    # 默认0.8s
    t = round(random.random() + 0.1, 1)
    time.sleep(t)


if __name__ == "__main__":
    main()
