# coding=utf-8
import sys
import re
import subprocess
import xml.etree.ElementTree as etree
import os
import Queue
import time
import math
import logging


reload(sys)
sys.setdefaultencoding("utf-8")
__author__ = 'WangZhe'

logging.basicConfig(level=logging.DEBUG,
                    format=' %(process)d: %(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='yinshi.log',
                    filemode='a')

tbfWord = ("吃".decode('utf-8'), "喝".decode('utf-8') )
xml_origin = {}
queue = Queue.PriorityQueue()


def pickup_file(file_name):
    logging.info("%s pickup begin" % (file_name))
    file = open(file_name, "r")
    file_write = open(file_name + ".ban", "w")
    xml_index = 0

    last_content = ""
    for index, line in enumerate(file):
        # id,uid,content,time,flag,username,male,location = line.strip().split("\t")
        is_food, food, content = line.strip().split("\t")
        if is_food == "1" and last_content != content:
            file_write.write(content + "\n")
        last_content = content

    file.close()
    file_write.close()
    return file_name + ".ban"


def split_sentence(content):
    punt_list = '.!?:;~。！？?…#：；～ ~!&"“”，,'.decode('utf-8')
    # punt_list =  '.!?;~。！？?…#；～ &~!'.decode('utf-8')
    # content = content.decode('utf-8')
    sentences = []
    sentence = ""

    for item in content.decode('utf-8'):
        sentence += item
        if item in punt_list:
            if len(sentence) > 3:
                sentences.append(sentence.encode('utf-8'))
            sentence = ""

    if len(sentence) > 3:
        sentences.append(sentence.encode('utf-8'))
    return sentences


def ban_rubbish(content):
    if re.search(".*http://.*", content):
        return ""
    if re.search("【.*?】", content):
        return ""

    m = re.findall("[\d①②③④]", content)
    if len(m) > 3:
        return ""

    content = re.subn("\[.*?\]", "", content)[0]
    content = re.subn("//@.*", "", content)[0]
    content = re.subn("//@.* ", "", content)[0]
    # content = re.subn("@.* ","",content)[0]
    content = re.subn("@.*", "", content)[0]
    # content = re.subn("@[0-8]* ","",content)[0]

    return content


def word_split_file(file_name):
    logging.info("%s word_split begin" % (file_name))
    fdout = open(file_name + ".ws_temp", 'w')
    fderr = open(file_name + ".ws_err", 'w')
    fdin = open(file_name, 'r')
    popen = subprocess.Popen("/users1/exe/bin/weicws", stdin=fdin, stdout=fdout, stderr=fderr, shell=True)
    popen.wait()
    fdout.close()

    fdin = open(file_name + ".ws_temp", 'r')
    fdout = open(file_name + ".ws", 'w')
    for line in fdin:
        fdout.write(line.replace("\t", " "))
    fdout.close()
    os.remove(file_name + ".ws_temp")
    return file_name + ".ws"


def dp_file(file_name):
    logging.info("%s dp begin" % (file_name))
    fdout = open(file_name + ".dp", 'w')
    fderr = open(file_name + ".dp_err", 'w')
    popen = subprocess.Popen(
        ["/users1/exe/bin/multi_ltp_test_wsed", "/data/yjliu/ltp-models/3.0.2/ltp.cnf", "dp", file_name],
        stdout=fdout, stderr=fderr, shell=False)
    popen.wait()
    return file_name + ".dp"


def xml_parse(content):
    nodes = []
    parser = etree.XMLParser(encoding="utf-8")

    tree = etree.fromstring(content, parser=parser)
    for node in tree.iter("word"):  #遍历解析树
        nodes.append({"id": node.attrib.get("id"),
                      "cont": node.attrib.get("cont"),
                      "pos": node.attrib.get("pos"),
                      "parent": node.attrib.get("parent"),
                      "relate": node.attrib.get("relate")})

    return nodes


def rule_handle(nodes):
    result = []
    for node in nodes:
        if node["relate"] == "VOB" \
                and node["pos"].find("n") != -1 \
                and (nodes[int(node["parent"])]["cont"] == "喝" or nodes[int(node["parent"])]["cont"] == "吃"):
            result.append([node["cont"], "1"])
        else:
            result.append([node["cont"], "0"])

    return result


def xml_read(file_name):
    logging.info("%s xml read begin" % (file_name))
    file = open(file_name, 'r')
    content = ""
    state = 0
    xml_index = 0
    result = []
    for line in file:
        if line == "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n":
            if len(content) > 0:
                try:
                    result.append(xml_parse(content))
                except Exception:
                    result.append([])
                finally:
                    content = ""
        else:
            content += line
    if len(content) > 0:
        result.append(xml_parse(content))
    file.close()
    return result


def get_final(file_name):
    logging.info("%s final begin" % (file_name))
    file = open(file_name, "r")
    file_write = open(file_name + ".result", "w")

    if not queue.empty():
        index, word = queue.get()
        for cur_index, line in enumerate(file):
            while cur_index == index:
                file_write.write(word + "\t\t" + line)
                if queue.empty():
                    file.close()
                    file_write.close()
                    return
                else:
                    index, word = queue.get()
                    logging.info("index:%d" % (index))

            if cur_index > index:
                if queue.empty():
                    break
                else:
                    index, word = queue.get()
    file.close()
    file_write.close()


def word_count(file_name):
    stop_word = set()
    with open("stop_word.txt", "r") as f:
        for line in f:
            stop_word.add(line.strip().decode("utf-8"))
    dict = {}
    with open(file_name, "r") as f:
        for line in f:
            words = line.strip().split(" ")
            for word in words:
                word = word.decode("utf-8")
                if word not in stop_word:
                    dict[word] = dict.get(word, 0) + 1

    result = sorted(dict.items(), key=lambda x: x[1], reverse=True)
    for key, value in result:
        print key, ":", value


def worker(file, id):
    file_name = pickup_file(file)

    file_name = word_split_file(file_name)

    file_name = dp_file(file_name)

    logging.info("%s xml parse begin" % (file))

    xmls = xml_read(file_name)
    for index, xml in enumerate(xmls):
        result = rule_handle(xml)
        for word in result:
            if word[1] == "1":
                queue.put((xml_origin[index], word[0]))

    get_final(file)


if __name__ == '__main__':
    start = time.time()
    logging.info("begin:%s" % (sys.argv[1]))

    file_name = pickup_file(sys.argv[1])
    file_name = word_split_file(file_name)
    word_count(file_name)
    end = time.time()
    logging.info("end process \n time cost:%d" % (end - start))

