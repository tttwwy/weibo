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
import urllib
import urllib2
import multiprocessing

from langconv import *
import base


reload(sys)
sys.setdefaultencoding("utf-8")
__author__ = 'WangZhe'


class Graph():
    graph = {}

    def clear(self):
        self.graph.clear()

    def add_node(self, name, value=0):
        self.graph[name] = self.graph.get(name, {"value": value, "edges": {}})

    def add_edge(self, A, B, weight=0):
        self.add_node(A, 1)
        self.add_node(B, 1)
        self.graph[A]["edges"][B] = self.graph[A]["edges"].get(B, 0) + weight
        self.graph[B]["edges"][A] = self.graph[B]["edges"].get(A, 0) + weight


class Rule(base.Base):
    rules = set()
    graph = Graph()
    keys = {}
    targets = {}
    partens = {}

    def pickup_file(self, file_name):
        logging.info("%s pickup begin" % (file_name))
        result_file_name = file_name + ".ban"
        with  open(file_name, "r") as file:
            with open(result_file_name, "w") as file_write:
                for index, line in enumerate(file):
                    content = line.strip().decode('utf-8')
                    content = self.ban_rubbish(content)
                    if content == "":
                        continue

                    for item in self.split_sentence(content):
                        for word in self.key_words:
                            if item.find(word) != -1:
                                item = Converter('zh-hans').convert(item)
                                file_write.write(item + "\n")
                                break

        return result_file_name



    def get_rule(self, nodes, is_train):
        target_words = []
        key_words = []
        for index, node in enumerate(nodes):
            flag = False
            for word in self.key_word:
                if node["cont"].find(word) != -1 and not self.is_food(node["cont"]) and  node["pos"] != "n":
                    key_words.append(index)
                    flag = True
                    break
            if not flag:
                if node["pos"] == "n" and (not is_train or self.is_food(node["cont"]) ):
                    target_words.append(index)
        if not target_words or not key_words:
            return []
        rules = []
        for target in target_words:
            min_way = []
            min_key = sys.maxint
            rule = {"key": "", "target": "", "way": []}
            rule["target"] = nodes[target]["cont"]
            # print rule["target"]

            for key in key_words:
                # print nodes[target]["cont"],nodes[key]["cont"]
                is_punt = False
                for i in range(target,key,1 if key > target else -1):
                    if nodes[i]["cont"] in self.punt_list_strict:
                        # print "die:",nodes[target]["cont"],nodes[key]["cont"]
                        is_punt = True
                        break
                if is_punt:
                    continue
                short_way = self.bfs(key, target, nodes)
                if len(short_way) < len(min_way) \
                        or len(min_way) == 0 \
                        or (len(short_way) == len(min_way) and abs(min_key - target) > abs(key - target)):
                    # print nodes[key]["cont"],nodes[target]["cont"],len(short_way)
                    min_way = short_way
                    min_key = key
                    rule["key"] = nodes[key]["cont"]

            if min_way:
                rule["way"] = min_way
                rules.append(rule)

        return rules

    def retrain_model(self, file_name):

        tree = self.xml_read(file_name)
        for nodes in tree:
            rules = self.get_rule(nodes, False)
            for rule in rules:
                A = rule["key"]
                B = rule["target"]
                parten = A + "".join(rule["way"])
                if parten:
                    # self.graph.add_node(A, 1)
                    self.graph.add_node(B, 1 if self.is_food(B) else 0)
                    self.graph.add_node(parten, 0)
                    self.keys[A] = 0
                    self.targets[B] = 0
                    self.partens[parten] = 0
                    # self.graph.add_edge(A, parten, 1)
                    self.graph.add_edge(parten, B, 1)
        # print self.graph.graph
        def get_m(x, y):
            result = self.graph.graph[x]["edges"][y] * 1.0 / sum(self.graph.graph[y]["edges"].values())
            # print result
            return result

        k = 0.7

        # 抽取规则置信度
        for x in self.partens:
            total_weight = sum(self.graph.graph[x]["edges"].values())
            total = sum([self.graph.graph[y]["value"] * self.graph.graph[y]["edges"][x] for y in self.graph.graph[x]["edges"].keys()])
            prc = total*1.0/total_weight
            self.graph.graph[x]["value"] = prc
            self.partens[x] = (prc,total)
            # print x,prc,total


        # for x in self.partens:
        #     total_weight = sum(self.graph.graph[x]["edges"].values())
        #     score = sum([get_m(x, y) * self.graph.graph[y]["value"] for y in self.graph.graph[x]["edges"].keys()])
        #     self.graph.graph[x]["value"] = score
        #     self.partens[x] = score

        # max_value = max(x for x in self.partens.values())
        # for key in self.partens:
        #     # print self.partens[key]
        #     self.partens[key] = self.partens[key] * 1.0 / max_value

        # for x in self.targets:
        #     print self.graph.graph[x]["edges"]
        # # 计算触发词置信度
        # for x in self.keys:
        #     self.keys[x] = sum([get_m(y, x) * self.graph.graph[y]["value"] * (1 - k) + k * 1 for y in
        #                         self.graph.graph[x]["edges"].keys()])
        #
        # # 计算目标词置信度
        # for x in self.targets:
        #     self.targets[x] = sum([get_m(y, x) * self.graph.graph[y]["value"] * (1 - k) + k * 1 for y in
        #                            self.graph.graph[x]["edges"].keys()])

        # max_value =  max([y for x,y in self.partens.values()])
        # for key in self.partens:
        #     print key,self.partens[key][0],self.partens[key][1],self.partens[key][1]*1.0/max_value

            # print sorted(self.partens.items(),key=lambda x:x[1][0],reverse=True),""
            # print sorted(self.partens.items(),key=lambda x:x[1][1],reverse=True),""



            # for key, value in sorted(self.keys.items(), key=lambda x: x[1], reverse=True):
            #     print key, value

            # for key,value in  sorted(self.targets.items(),key=lambda x:x[1],reverse=True):
            #     print key,value
            # for item in self.keys:
            #     print item

    # def train_model(self, file_name):
    #     # file_name = self.pickup_file(file_name)
    #     # file_name = self.word_split_file(file_name)
    #     # file_name = self.pos_file(file_name)
    #     # file_name = self.dp_file(file_name)
    #     tree = self.xml_read(file_name)
    #     for nodes in tree:
    #         rules = self.get_rule(nodes, True)
    #         for rule in rules:
    #             rule_text = rule["key"] + "".join(rule["way"])
    #             if rule_text:
    #                 A = rule["key"]
    #                 B = rule["target"]
    #                 parten = "".join(rule["way"])
    #
    #                 self.keys[A] = 0
    #                 self.targets[B] = 0
    #                 self.partens[parten] = 0
    #                 self.graph.add_edge(A, parten, 1)
    #                 self.graph.add_edge(parten, B, 1)
    #                 # print A,parten
    #
    #
    #                 self.rules.add(rule_text)
    #
    #     def get_m(x, y):
    #         return self.graph.graph[x]["edges"][y] * 1.0 / sum(self.graph.graph[x]["edges"].values())
    #
    #     for x in self.partens:
    #         self.partens[x] = sum(
    #             [get_m(x, y) * self.graph.graph[x]["value"] for y, weight in self.graph.graph[x]["edges"].items()])
    #
    #     # max_value = max(x for x in self.partens.values())
    #     # for key in self.partens:
    #     #     # print self.partens[key]
    #     #     self.partens[key] = self.partens[key] * 1.0 / max_value
    #
    #     print sorted(self.partens.items(), key=lambda x: x[1], reverse=True)
    # # for item in self.keys:
    # #     print item
    #

    def test(self, nodes):
        rules = self.get_rule(nodes, False)
        targets = []
        for rule in rules:
            rule_text = rule["key"] + "".join(rule["way"])
            print rule_text
            if self.partens.get(rule_text,(0,0)) >= (0.5,10):
                # print self.partens[rule_text],rule_text,rule["target"]
                targets.append(rule["target"])
        return targets

    def save_model(self, file_name):
        with open(file_name, "w") as f:
            for parten,(prc,total) in self.partens.items():
                f.write("{0} {1} {2}\n".format(parten.decode("utf-8"),prc,total))
                # f.write(parten.decode("utf-8") + "\n")

    def load_model(self, file_name):
        self.partens.clear()
        with open(file_name, "r") as f:
            for line in f:
                parten,prc,total = line.strip().split(" ")
                self.partens[parten.decode("utf-8")] = (float(prc),int(total))
        # print self.partens

    def ltp(self, sentence, type):

        url_base = "http://api.ltp-cloud.com/analysis/?"
        data = {
            "api_key": "27R3c63W8Bms2FDfZk2jAdGcXiKafybgVJ7rCE0r",
            "text": sentence,
            "format": "xml",
            "pattern": type,
            "xml_input": "false"
        }
        params = urllib.urlencode(data)
        request = urllib2.Request(url_base)
        response = urllib2.urlopen(request, params)
        content = response.read()
        # print content
        nodes = self.xml_parse(content)
        return nodes

    def gen_standard(self,fi,fo):
        with open(fo,"w") as f:
            for nodes in rule.xml_read(fi):
                foods = []
                sentence = ""
                for node in nodes:
                    if node["pos"] == "n":
                        foods.append((node["cont"],1 if self.is_food(node["cont"]) else 0))
                    sentence += node["cont"]
                for food,is_food in foods:
                    f.write("{0}\t{1}\t{2}\n".format(food,is_food,sentence))

    def gen_dict(self,fi,fo):
        with open(fo,"w") as f:
            for nodes in self.xml_read(fi):
                foods = []
                sentence = ""
                for node in nodes:
                    if node["pos"] == "n":
                        foods.append((node["cont"],1 if self.is_food(node["cont"]) else 0))
                    sentence += node["cont"]
                for food,is_food in foods:
                    f.write("{0}\t{1}\t{2}\n".format(is_food,food,sentence))

    def gen_rule(self,fi,fo,prc_num=0,total_num=0):
        with open(fo,"w") as f:
            for nodes in self.xml_read(fi):
                sentence = ""
                targets = []
                for node in nodes:
                    if node["pos"] == "n":
                        targets.append(node["cont"])
                    sentence += node["cont"]
                rules = self.get_rule(nodes, False)
                index = 0
                for target in targets:
                    rule_text = ""
                    food = target
                    is_food = 0
                    if index < len(rules) and rules[index]["target"] == target:
                        rule_text = rules[index]["key"] + "".join(rules[index]["way"])
                        prc,total = self.partens.get(rule_text,(0,0))
                        is_food = 1 if   prc > prc_num and total > total_num else 0
                        index += 1
                    f.write("{0}\t{1}\t{2}\t{3}\n".format(is_food,food,sentence,rule_text))




if __name__ == '__main__':
    rule = Rule()
    rule.add_dict("dict/dict.txt")
    rule.add_dict("dict/ws_dict.txt")
    print "begin:train"
    # rule.retrain_model("data/18500001--18600000--weibo-user.txt_0.ban.ws.pos.dp")
    # rule.retrain_model("data/yuliao.txt_0.ban.ws.pos.dp")
    # rule.save_model("rule_model.txt")
    rule.load_model("rule_model.txt")
    # nodes = rule.ltp("喝豆浆加红糖喝起来味甜香,但红糖里的有机酸和豆浆中的蛋白质结合后,可产生变性沉淀物,大大破坏了营养成分,因此喝豆浆时不要加红糖.","dp")
    # sentence = ""
    #
    # targets = []
    #
    #
    # for node in nodes:
    #     if node["pos"] == "n":
    #         targets.append(node["cont"])
    #     sentence += node["cont"]
    #
    # rules = rule.get_rule(nodes, False)
    # index = 0
    # for target in targets:
    #     rule_text = ""
    #     food = target
    #     is_food = 0
    #     if index < len(rules) and rules[index]["target"] == target:
    #         rule_text = rules[index]["key"] + "".join(rules[index]["way"])
    #         is_food = 1 if rule.partens.get(rule_text,(0,0)) >= (0.5,10) else 0
    #         index += 1
    #     print is_food,food,sentence,rule_text
        # f.write("{0}\t{1}\t{2}\t{3}\n".format())

    # print "begin get rule"
    # for key in rule.partens:
    #     print key,rule.partens[key][0],rule.partens[key][1]
    rule.gen_rule("data/yuliao.txt_0.ban.ws.pos.dp","newdata/rule.txt")
    # print rule.judge("newdata/standard.txt","newdata/dict.txt")
    print rule.judge("newdata/standard.txt","newdata/rule.txt")

    # for nodes in rule.xml_read("data/yuliao.txt_0.ban.ws.pos.dp"):
    #     rule.test(nodes)
    # sentences = rule.split_sentence("我想吃西瓜还有苹果".decode("utf-8"))
    # for sentence in sentences:
    #     # print sentence
    #     nodes = rule.ltp(sentence,"dp")
    #     for item in  rule.test(nodes):
    #         print item