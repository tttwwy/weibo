# coding=utf-8
import MySQLdb
import crf
import rule
from langconv import *


reload(sys)
sys.setdefaultencoding("utf-8")
__author__ = 'WangZhe'
table_name = "basic_data"


def get_new_word(file_name):
    dict = {}
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip().split("\t")
            for word in line:
                word = word.decode("utf-8")
                dict[word] = dict.get(word, 0) + 1

    result = sorted(dict.iteritems(), key=lambda x: x[1], reverse=True)
    for key, value in result:
        if (len(key) == 1 and value > 50) or (len(key) > 1 and value > 1):
            print key, value


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

if __name__ == '__main__':
    rules = rule.Rule()
    rules.add_dict("dict/dict.txt")
    rules.add_dict("dict/ws_dict.txt")


    #
    # print "begin:train"
    rules.gen_dict("data/mix_dp.txt","newdata/dict.txt")
    print rules.judge("newdata/mix_standard.txt","newdata/dict.txt")
    #
    #
    #
    rules.load_model("rule_model.txt")
    rules.gen_rule("data/mix_dp.txt","newdata/rule.txt",0.5,10)
    print rules.judge("newdata/mix_standard.txt","newdata/rule.txt")



    crf = crf.CRF()
    crf.read_rule_model("rule_model.txt")
    crf.train("data/yuliao.txt_0.ban.ws.pos.dp","newdata/standard.txt","model.txt")
    # crf.train("data/mix_dp.txt","newdata/mix_standard.txt","model.txt")

    crf.gen_rule("model.txt","data/mix_dp.txt","newdata/crf.txt")
    print crf.judge("newdata/mix_standard.txt","newdata/crf.txt")
