__author__ = 'Administrator'
# coding=utf-8


import sys
import struct
import math
import time
import urllib2
import Queue
import urllib

reload(sys)
sys.setdefaultencoding("utf-8")


class WordVector:
    model = {}

    def get_sentence_dis(self, a, b):
        a = a.strip().split(" ")
        b = b.strip().split(" ")
        A_sum_dis = 0
        B_sum_dis = 0
        for A in a:
            max_dis = 0
            for B in b:
                dis = self.get_word_dis(A, B)
                if dis > max_dis:
                    max_dis = dis
            A_sum_dis += max_dis

        for B in b:
            max_dis = 0
            for A in a:
                dis = self.get_word_dis(A, B)
                if dis > max_dis:
                    max_dis = dis
            B_sum_dis += max_dis

        return (A_sum_dis / len(a) + B_sum_dis / len(b) ) * 0.5


    def get_word_dis(self, a, b):
        # print a,b
        A = self.model.get(a.decode('utf-8'), [])
        B = self.model.get(b.decode('utf-8'), [])
        result = 0.0
        # print A,B
        for x, y in zip(A, B):
            result += x * y
        return result

    def read_model(self, file_name):
        max_size = 2000
        N = 40
        max_w = 50
        with open(file_name, "rb") as f:
            word_num, vec_size = f.readline().strip().split(" ")
            word_num = int(word_num)
            vec_size = int(vec_size)
            print word_num
            print word_num, vec_size

            for word_index in range(word_num):
                str = ""
                while 1:
                    ch = f.read(1)
                    if ch != ' ':
                        str += ch
                    else:
                        # ch = f.read(1)
                        break
                list = []
                for i in range(vec_size):
                    temp = f.read(4)
                    weight = struct.unpack('f', temp)[0]
                    list.append(weight)
                str = str.strip().decode('utf-8', 'ignore')
                len = 0.0000000
                for index, item in enumerate(list):
                    len += item * item
                len = math.sqrt(len)
                for index, item in enumerate(list):
                    list[index] = list[index] / len
                self.model[str] = list


class Graph:
    node = {"root": (0, 1, {"root1": 4})}

    def add_node(self, key, type, value):
        self.node[key] = self.node.get(key, (type, value, {}))

    def add_edge(self, A, B, weight=0.0):
        if A != B:
            self.node[A] = self.node.get(A, (0, 0, {}))
            self.node[A][2][B] = weight

            self.node[B] = self.node.get(B, (0, 0, {}))
            self.node[B][2][A] = weight


def ws(sentence):
    url_base = "http://api.ltp-cloud.com/analysis/?"
    data = {
        "api_key": "27R3c63W8Bms2FDfZk2jAdGcXiKafybgVJ7rCE0r",
        "text": sentence,
        "format": "xml",
        "pattern": "dp",
        "xml_input": "false"
    }
    params = urllib.urlencode(data)
    request = urllib2.Request(url_base)
    response = urllib2.urlopen(request, params)
    content = response.read()
    return content

# print ws("我是\n中国\n人")
#
#
# print time.time()
wordvector = WordVector()
wordvector.read_model("data/vectors.bin")
print "read model finished!"
# print time.time()
#
#
# threshold = 0.6
# graph = Graph()
# queue = Queue.Queue()
# result = set()
# # with open("seed_word.txt","r") as f:
# #     for line in f:
# #         queue.put(line.strip().decode('utf-8'))
# queue.put("西瓜".decode('utf-8'))
# # for word in seed_word:
# #     graph.add_node(word,1,1.0)
#
# list = wordvector.model.keys()
# index = 0
# while not queue.empty():
#     cur_word = queue.get()
#     print index,cur_word
#     index += 1
#     result.add(cur_word)
#     for word in list:
#         if word != cur_word:
#             dis = wordvector.get_word_dis(cur_word,word)
#             if dis > threshold and word not in result:
#                 queue.put(word)

#
# index = 0
#
#
# size_list = len(list)
# for i in xrange(size_list):
#     for j in xrange(i,size_list):
#         print i,j
#         A = list[i]
#         B = list[j]
#         dis = wordvector.get_word_dis(A,B)
#         if dis > threshold:
#             graph.add_edge(A,B,dis)

# for word in :
#     for node in graph.node.keys():
#         dis = wordvector.get_word_dis(word,node)
#         if dis > threshold:
#             graph.add_edge(word,node,dis)
#             print index,word
#             index += 1


while (1):
    # a = ws(raw_input().strip())
    # b = ws(raw_input().strip())
    a = raw_input().strip()
    b = raw_input().strip()
    print wordvector.get_sentence_dis(a, b)

