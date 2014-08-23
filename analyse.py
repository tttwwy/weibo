__author__ = 'WangZhe'
# coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

dict = {}


def word_count(file_name):
    result = {}
    file = open(file_name, "r")
    for line in file:
        word = line.strip().split("\t")[0]

        if word in result.keys():
            result[word] += 1
        else:
            result[word] = 1
            # print result
    return sorted(result.iteritems(), key=lambda d: d[1], reverse=True)


result = word_count(sys.argv[1])
for key, value in result:
    print key, ":", value