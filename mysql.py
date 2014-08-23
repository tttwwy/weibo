# coding=utf-8
__author__ = 'Administrator'
import sys
import re
import datetime
import math

import MySQLdb

from langconv import *


reload(sys)
sys.setdefaultencoding("utf-8")

db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="yinshi", charset="utf8")
cursor = db.cursor()

table_name = "basic_data_new"


def insert(id, word, province, city, sex, createtime, content, hour, month):
    content.decode("utf-8")
    sql = "insert into basic_data_new(food,province,city,sex,createtime,content,user_id,hour,month) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    n = cursor.execute(sql, (word, province, city, sex, createtime, content, id, hour, month))
    # conn.commit()


def read(file_name):
    word_count = {}
    with open(file_name, "r") as f:
        for index, line in enumerate(f):

            word, id, content, createtime, location, sex = re.split("\t+", line.strip())

            province = ""
            city = ""
            # content = Converter('zh-hans').convert(content.decode('utf-8')).encode('utf-8')
            content = content.decode('utf-8').encode('utf-8')
            location = location.split(" ")
            if len(location) == 1:
                province = location[0]
            if len(location) == 2:
                province, city = location
            create_time = datetime.datetime.strptime(createtime, "%Y-%m-%d %H:%M:%S")
            hour = int(create_time.hour)
            month = int(create_time.month)
            insert(id, word, province, city, sex, createtime, content, hour, month)
            # temp = []
            # if not word_count.has_key(word):
            #     word_count[word] = []
            # word_count[word].append( (id,word,province,city,sex,createtime,content,hour,month) )


            print index

    db.commit()


def read_dict(file_name):
    dict = {}
    with open(file_name, "r") as f:
        for line in f:
            line = line.strip()
            sql = "insert into yinshi_dict(food) values(%s)"
            cursor.execute(sql, (line,))


def read_analyse(file_name):
    dict = {}
    with open(file_name, "r") as f:
        for line in f:
            word, id, content, createtime, location, sex = re.split("\t+", line.strip())
            content = content.decode("utf-8")
            for word in content:
                dict[word] = dict.get(word, 0) + 1
    list = sorted(dict.items(), lambda x, y: cmp(x[1], y[1]))
    for key, value in list:
        print key.encode("utf-8"), value


# read_analyse("C:\\Users\\Administrator\\Desktop\\result.txt")
def insert_data():
    file = open("result", "r")
    for index, line in enumerate(file):
        food, id, uin, content, times, sex, username, flag, location = line.strip().split("\t")
        create_time = datetime.datetime.strptime(times, "%a %b %d %H:%M:%S CST %Y")
        province = ""
        city = ""
        if sex == "1":
            sex = "男"
        if sex == "2":
            sex = "女"
        location = location.strip().split(" ")
        if len(location) > 1:
            province, city = location
            # print province,city
        elif len(location) == 1:
            province = location[0]

        content = Converter('zh-hans').convert(content.decode('utf-8')).encode('utf-8')

        # print int(time.mktime(date))
        sql = '''insert into %s (uin,time,sex,province,city,content,food) values
                    (%s,'%s','%s','%s','%s',"%s",'%s')''' % (
        table_name, uin, create_time, sex, province, city, content, food)
        # print sql
        print index
        try:
            cursor.execute(sql)

        except:
            pass
        finally:
            # db.close()
            pass
    db.commit()
    db.close()


def insert_dict():
    db = MySQLdb.connect("localhost", "root", "root", "yinshi", charset='utf8')
    cursor = db.cursor()
    with open("dict.txt") as f:
        for line in f:
            sql = "insert into yinshi_dict(food) values('%s')" % (line.strip())
            print sql
            try:
                cursor.execute(sql)
            except:
                pass
    db.commit()


read("C:\\Users\\Administrator\\Desktop\\result.txt")