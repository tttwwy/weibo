# coding=utf-8

import re
import subprocess
import xml.etree.ElementTree as etree
import os
import Queue
import time
import math
import logging
import multiprocessing

from langconv import *

__author__ = 'WangZhe'

logging.basicConfig(level=logging.DEBUG,
                    format=' %(process)d: %(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='yinshi.log',
                    filemode='a')


class Base():
    dict = set()

    key_word = (	"吃".decode('utf-8'),
                    "喝".decode('utf-8'),
                    "食".decode('utf-8'),
                    "味".decode('utf-8'),
                    "炒".decode('utf-8'),
                    "饭".decode('utf-8'),
                    "香".decode('utf-8'),
                    "杯".decode('utf-8'),
                    "尝".decode('utf-8'),
                    "饿".decode('utf-8'),
                    "菜".decode('utf-8'),
                    "餐".decode('utf-8'),
                    "煮".decode('utf-8'),
                    "泡".decode('utf-8'),
                    "饱".decode('utf-8')	)
    punt_list_strict =  '.!?:;~。！？?…#：；～ ~!&"“”，，,'.decode('utf-8')
    punt_list = '!?;~。！？?…#；～ &~!'.decode('utf-8')


    def add_dict(self, file_name):
        logging.info("init_dict begin")
        with open(file_name, "r") as f:
            for line in f:
                line = line.strip().decode("utf-8")
                Base.dict.add(line)

        logging.info("init_dict end")

    # def is_food(self, food):
    #     food = food.decode('utf-8')
    #     left = 0
    #     max = len(food)
    #     right = max
    #     while left < right and right > 0:
    #         if food[left:right] in self.dict:
    #             return True
    #         right -= 1
    #     return False

    def is_food(self, food):
        food = food.decode('utf-8')
        return food in self.dict

    def ban_rubbish(self, content):
        content = u"<title>(.*)"
        re.search(ans+"", content)
        if re.search(u".*http://.*", content):
            # logging.info("ban:http url:{0}".format(content))
            return ""
        if re.search(u"【.*?】", content):
            # logging.info("bazen:【】:{0}".format(content))
            return ""

        m = re.findall(u"[①②③④]", content)
        if len(m) > 2:
            logging.info(u"ban:①②③④:{0}".format(content))
            for item in m:
                logging.info(u"ban:①②③④:{0}".format(item))
            return ""

        content = re.subn(u"\[.*?\]", "", content)[0]
        content = re.subn(u"//@.*", "", content)[0]
        content = re.subn(u"//@.* ", "", content)[0]
        # content = re.subn("@.* ","",content)[0]
        content = re.subn(u"@.*", "", content)[0]
        # content = re.subn("@[0-8]* ","",content)[0]
        return content

    def split_sentence(self, content):
        sentences = []
        sentence = ""

        for item in content:
            sentence += item
            if item in self.punt_list:
                if len(sentence) > 3:
                    sentences.append(sentence)
                sentence = ""

        if len(sentence) > 3:
            sentences.append(sentence)
        return sentences


    def word_split_file(self, file_name):
        logging.info("%s word_split begin" % (file_name))
        fdout = open(file_name + ".ws_temp", 'w')
        fderr = open(file_name + ".ws_err", 'w')
        fdin = open(file_name, 'r')
        popen = subprocess.Popen("/users1/exe/bin/weicws", stdin=fdin, stdout=fdout, stderr=fderr, shell=True)
        popen.wait()
        fdout.close()
        fdin.close()

        fdin = open(file_name + ".ws_temp", 'r')
        fdout = open(file_name + ".ws", 'w')
        for line in fdin:
            fdout.write(self.ws_word_combine(line) + "\n")
        fdout.close()
        fdin.close()
        # os.remove(file_name + ".ws_temp")
        return file_name + ".ws"


    def ws_word_combine(self, words):
        result = ""
        # print len(dict)
        words = words.strip().split("\t")
        last_flag = False
        cur_flag = False
        for index, word in enumerate(words):

            cur_flag = word.decode('utf-8') in self.dict
            # print word,cur_flag
            if last_flag == False and len(word.decode('utf-8 ')) == 1:
                cur_flag = False
            if index == 0 or last_flag == cur_flag == True:
                result += word
            else:
                result += "\t" + word
            last_flag = cur_flag
        return result

    def pos_word_combine(self, line):
        result = ""
        line = [x.split("|") for x in line.strip().split("\t")]
        flag = -1
        for index, (word, pos) in enumerate(line):
            is_n = pos in ("n", "nh", "ni", "nz")
            if is_n and flag >= 0:
                line[flag][0] += word
                line[flag][1] = "n"
                line[index][1] = "0"
            elif is_n and flag < 0:
                flag = index
            else:
                flag = -1

        for index, (word, pos) in enumerate(line):
            if pos != "0":
                result += "{0}{1}|{2}\t".format(" " if index > 0 else "", word, pos)
        return result



    def pos_file(self, file_name):
        logging.info("%s pos begin" % (file_name))
        fdout = open(file_name + ".pos", 'w')
        fderr = open(file_name + ".pos_err", 'w')
        popen = subprocess.Popen(
            ["/users1/bren/zhew/ltp/ltp-master/examples/pos", "/users1/exe/bin/3.1.0/ltp_data/pos.model", file_name],
            stdout=fdout, stderr=fderr, shell=False)
        popen.wait()
        logging.info("%s pos end" % (file_name))
        fdout.close()

        return file_name + ".pos"


    def dp_file(self, file_name):
        logging.info("%s dp begin" % (file_name))
        fdout = open(file_name + ".dp", 'w')
        fderr = open(file_name + ".dp_err", 'w')
        popen = subprocess.Popen(
            ["/users1/exe/bin/zwang/ltp_pos_parser", "/users1/exe/bin/3.1.0/ltp_data/ltp.cnf", file_name],
            stdout=fdout, stderr=fderr, shell=False)
        popen.wait()
        logging.info("%s dp end" % (file_name))
        return file_name + ".dp"


    def xml_parse(self, content):
        nodes = []
        parser = etree.XMLParser(encoding="utf-8")

        tree = etree.fromstring(content, parser=parser)
        for node in tree.iter("word"):  #遍历解析树
            nodes.append({"id": int(node.attrib.get("id")),
                          "cont": node.attrib.get("cont").decode('utf-8'),
                          "pos": node.attrib.get("pos"),
                          "parent": int(node.attrib.get("parent")),
                          "relate": node.attrib.get("relate")})

        return nodes

    def xml_read(self, file_name):
        logging.info("%s xml read begin" % (file_name))
        with  open(file_name, 'r') as file:
            content = ""
            for line in file:
                if line == "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n":
                    if len(content) > 0:
                        try:
                            yield self.xml_parse(content)

                        except Exception:
                            yield []
                        finally:
                            content = ""
                else:
                    content += line
        if len(content) > 0:
            yield self.xml_parse(content)
        logging.info("%s   xml read end" % (file_name))
    def bfs(self, x, y, nodes):
        # print nodes[x]["cont"],nodes[y]["cont"]
        graph = {}
        for node in nodes:
            A = node["id"]
            B = node["parent"]
            weight = node["relate"]
            graph[A] = graph.get(A, {})
            graph[A][B] = weight
            graph[B] = graph.get(B, {})
            graph[B][A] = weight

        queue = Queue.Queue()
        flag = {}
        queue.put(x)
        list = []
        visited = set()
        rule = []
        # print graph
        while not queue.empty():
            cur = queue.get()
            visited.add(cur)
            if cur != y:
                for id, weight in graph[cur].items():
                    if id not in visited:
                        queue.put(id)
                        flag[id] = (cur, weight)
            else:
                pre = flag.get(cur)
                # list.insert(0,(cur,""))
                while pre:
                    list.insert(0, pre)
                    # print "pre:",pre
                    pre = flag.get(pre[0])
                # print list
                break
                # print cur
        for (index, relate) in list:
            if index == x:
                rule.append(relate)
            else:
                rule.append(nodes[index]["pos"])
                rule.append(relate)

        return rule


    def judge(self,standard_file_name,test_file_name):
        with open(standard_file_name,"r") as f1:
            with open(test_file_name,"r") as f2:
                A = 0
                B = 0
                C = 0
                for standard in f1:
                    standard_flag = standard.strip().split("\t")[0]
                    test = f2.readline()
                    test_flag = test.strip().split("\t")[0]
                    if standard_flag == test_flag == "1":
                        A += 1
                    elif standard_flag == "0" and  test_flag == "1":
                        B += 1
                    else:
                        if standard_flag == "1" and test_flag == "0":
                            C += 1
                        # print standard,test

                print A,B,C
                R = A * 1.0 / (A + C)
                P = A * 1.0 / (A + B)
                F = 2 * R * P / (R + P)

        return (R,P,F)
