# coding=utf-8
import subprocess
import logging

from langconv import *
import pickup
import base

reload(sys)
sys.setdefaultencoding("utf-8")
__author__ = 'WangZhe'

logging.basicConfig(level=logging.DEBUG,
                    format=' %(process)d: %(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='yinshi.log',
                    filemode='a')


class CRF(base.Base):
    model_name = ""
    rule_model = {}
    def read_rule_model(self,file_name):
        with open(file_name,"r") as f:
            for line in f:
                line = line.strip().decode("utf-8").split(" ")
                self.rule_model[line[0]] = float(line[1])

    # def get_rule(self,nodes):
    #     targets = []
    #     for node in nodes:
    #         if node["pos"] == "n":
    #             targets.append(node["id"])
    #
    #
    #     def get_target_rule(target):
    #         key_word = "NULL"
    #         key_word_pos = "NULL"
    #         key_word_index = -1
    #         short_way = "NULL"
    #         time_word = "NULL"
    #         index = target - 1
    #         while index >= 0 and nodes[index]["cont"] not in self.punt_list_strict:
    #             for key in self.key_word:
    #                 if nodes[index]["cont"].find(key) != -1 and len(nodes[index]["cont"]) <= 4:
    #                     key_word = nodes[index]["cont"]
    #                     key_word_pos = nodes[index]["pos"]
    #                     key_word_index = index
    #                     break
    #             index -= 1
    #         index = target + 1
    #         while index < len(nodes) and nodes[index]["cont"] not in self.punt_list_strict:
    #             for key in self.key_word:
    #                 if nodes[index]["cont"].find(key) != -1:
    #                     key_word = nodes[index]["cont"]
    #                     key_word_pos = nodes[index]["pos"]
    #                     key_word_index = index
    #                     break
    #             index += 1
    #
    #         if key_word != "NULL":
    #             way = self.bfs(key_word_index,target,nodes)
    #             if way:
    #                 short_way = "".join(way)
    #
    #         for node in nodes:
    #             if node["pos"] == "nt":
    #                 time_word = node["cont"]
    #                 break
    #         return (key_word,key_word_pos,short_way,time_word)
    #     rules = []
    #     for target in targets:
    #         rule = get_target_rule(target)
    #
    #         rules.append({"rule":rule,"target":nodes[target]["cont"]})
    #
    #     return rules

    def get_rule(self,nodes):
        targets = []
        for node in nodes:
            if node["pos"] == "n":
                targets.append(node["id"])


        def get_target_rule(target):
            key_word = "NULL"
            key_word_pos = "NULL"
            key_word_index = -1
            short_way = "NULL"
            time_word = "NULL"
            rule_prc = "0"
            index = target - 1
            while index >= 0 and nodes[index]["cont"] not in self.punt_list_strict:
                for key in self.key_word:
                    if nodes[index]["cont"].find(key) != -1 and len(nodes[index]["cont"]) <= 4:
                        key_word = nodes[index]["cont"]
                        key_word_pos = nodes[index]["pos"]
                        key_word_index = index
                        break
                index -= 1
            index = target + 1
            while index < len(nodes) and nodes[index]["cont"] not in self.punt_list_strict:
                for key in self.key_word:
                    if nodes[index]["cont"].find(key) != -1:
                        key_word = nodes[index]["cont"]
                        key_word_pos = nodes[index]["pos"]
                        key_word_index = index
                        break
                index += 1

            if key_word != "NULL":
                way = self.bfs(key_word_index,target,nodes)
                if way:
                    short_way = "".join(way)

            for node in nodes:
                if node["pos"] == "nt":
                    time_word = node["cont"]
                    break
            rule_prc = self.rule_model.get(key_word + short_way,0)
            rule_prc = str(rule_prc * 10 / 1)
            is_food = self.is_food(nodes[target]["cont"])
            # time_word = is_food
            return (key_word,short_way,time_word,rule_prc)
        rules = []
        for target in targets:
            rule = get_target_rule(target)

            rules.append({"rule":rule,"target":nodes[target]["cont"]})

        return rules


    def train(self,file_name,standard_name,model_name):
        train_file = "train.txt"
        standard_file = []
        with open(standard_name,"r") as f:
            for line in f:
                if line.strip():
                    standard_file.append(line.strip().split("\t")[0])
                    # print line.strip().split("\t")[0]
        index = 0
        with open(train_file,"w") as f:
            for nodes in self.xml_read(file_name):
                rules = self.get_rule(nodes)
                for rule in rules:
                        # is_food = 1 if self.is_food(rule["target"]) else 0
                        is_food = standard_file[index]
                        # print is_food
                        index += 1
                        f.write("{0} {1[0]} {1[1]} {1[2]} {1[3]} {2}\n".format(rule["target"],rule["rule"],is_food))


        fdout = open(model_name, 'w')
        fderr = open(model_name + ".err", 'w')
        # popen = subprocess.Popen(["/users1/bren/crf++/bin/crf_learn", "-c", "4.0", "template", train_file, model_name],
        #                          stdout=fdout, stderr=fderr, shell=False)

        popen = subprocess.Popen(["H:\Program\CRF++-0.58\crf_learn.exe", "-c", "4.0", "H:\\Program\\CRF++-0.58\\train\\template", train_file, model_name],
                                 stdout=fdout, stderr=fderr, shell=False)

        popen.wait()

    def gen_rule(self,model_name,file_name,file_out_name):
        with open("temp","w") as f:
            for nodes in self.xml_read(file_name):
                rules = self.get_rule(nodes)
                for rule in rules:
                        is_food = 1 if self.is_food(rule["target"]) else 0
                        f.write("{0} {1[0]} {1[1]} {1[2]} {1[3]}\n".format(rule["target"],rule["rule"]))

        self.test(model_name,"temp","temp1")
        with open("temp1","r") as f:
            with open(file_out_name,"w") as f2:
                for line in f:
                    if line.strip():
                        line = line.strip().split("\t")
                        word = line[0]
                        is_food = line[5]
                        f2.write("{0}\t{1}\n".format(is_food,word))

    #
    #
    # def crf_handle(self,nodes):
    #     result = []
    #     left_verbs = []
    #     right_verbs = []
    #
    #     verb = "NULL"
    #     for node in nodes:
    #         left_verbs.append(verb)
    #         if node["pos"] == "v":
    #             verb = node["cont"]
    #
    #     verb = "NULL"
    #     for node in nodes[::-1]:
    #         right_verbs.append(verb)
    #         if node["pos"] == "v":
    #             verb = node["cont"]
    #     right_verbs.reverse()
    #
    #     for index, node in enumerate(nodes):
    #         word = "NULL"
    #         pos = "NULL"
    #         left_verb = "NULL"
    #         right_verb = "NULL"
    #         father_word = "NULL"
    #         father_pos = "NULL"
    #         father_relate = "NULL"
    #         food = "0"
    #         # if is_food(node["cont"].decode('utf-8').encode('utf-8')):
    #         #     food = "1"
    #         word = node["cont"]
    #         pos = node["pos"]
    #         left_verb = left_verbs[index]
    #         right_verb = right_verbs[index]
    #         father_word = nodes[int(node["parent"])]["cont"]
    #         father_pos = nodes[int(node["parent"])]["pos"]
    #         father_relate = node["relate"]
    #         # result.append(word+"\t"+pos+"\t"+left_verb+"\t"+right_verb+"\t"+father_word+"\t"+father_pos+"\t"+father_relate+"\t")
    #         result.append([word, pos, left_verb, right_verb, father_word, father_pos, father_relate])
    #
    #         # logging.info(word+"\t"+pos+"\t"+left_verb+"\t"+right_verb+"\t"+father_word+"\t"+father_pos+"\t"+father_relate+"\t")
    #     return result


    def test(self,model_name,file_name,file_out_name):


        fdout = open(file_out_name, 'w')
        fderr = open(file_name + ".test_err", 'w')
        # popen = subprocess.Popen(["/users1/bren/crf++/bin/crf_test", "-m", model_name, file_name],
        #                          stdout=fdout, stderr=fderr, shell=False)

        popen = subprocess.Popen(["H:\Program\CRF++-0.58\crf_test.exe", "-m", model_name, file_name],
                                 stdout=fdout, stderr=fderr, shell=False)

        popen.wait()


if __name__ == '__main__':

    crf = CRF()
    crf.add_dict("dict/dict.txt")
    crf.add_dict("dict/ws_dict.txt")
    # crf.train("data/yuliao.txt_0.ban.ws.pos.dp","model.txt")
    crf.train("data/18500001--18600000--weibo-user.txt_0.ban.ws.pos.dp","model.txt")

    crf.gen_rule("model.txt","data/yuliao.txt_0.ban.ws.pos.dp","newdata/crf.txt")
    print crf.judge("newdata/standard.txt","newdata/crf.txt")
    # crf.test("model.txt","data/yuliao.txt_0.ban.ws.pos.dp","newdata/crf.txt")


