# coding=utf-8
import sys
import random

import pickup
import crf

reload(sys)
sys.setdefaultencoding("utf-8")
food_dict = set()


def init_dict(dict_name):
    global food_dict
    file = open(dict_name, "r")
    for line in file:
        line = line.strip()
        food_dict.add(line)


def form_yuliao(file_name):
    file = open(file_name, "r")
    file_write = open("train.txt", "w")
    last_word = ""
    for line in file:
        temp = line.strip().split("\t")
        flag = temp[0][0]
        word = temp[2]
        if last_word == "":
            last_word = word
        else:
            if word == last_word:
                continue
            else:
                last_word = word
        for index, word in enumerate(temp):
            if index == 0 or index == 1:
                continue

            is_food = "0"
            if flag == "1" and word in food_dict:
                is_food = "1"
            file_write.write(word + " " + is_food + "\t")

        file_write.write("\n")


def wc(file_name):
    file_name = pickup.word_split_file(file_name)
    file = open(file_name, "r")
    file_write = open("wc.txt", "w")
    for line in file:
        line = line.strip().split(" ")
        for word in line:
            flag = "0"
            if word in food_dict:
                flag = "1"
            file_write.write(word + " " + flag + "\t")
        file_write.write("\n")
    file_write.close()


def dp(file_name):
    file_name = pickup.word_split_file(file_name)
    file_name = pickup.dp_file(file_name)
    xmls = pickup.xml_read(file_name)
    file_write = open("dp.txt", "w")
    for xml in xmls:
        result = pickup.rule_handle(xml)
        for word, flag in result:
            file_write.write(word + " " + flag + "\t")
        file_write.write("\n")
    file_write.close()


def dp_word(file_name):
    file_name = pickup.word_split_file(file_name)
    file_name = pickup.dp_file(file_name)
    xmls = pickup.xml_read(file_name)
    file_write = open("dp.txt", "w")
    for xml in xmls:
        result = pickup.rule_handle(xml)
        for word, flag in result:
            if flag == "1" and word.decode("utf-8").encode("utf-8") not in food_dict:
                # pass
                # print len(food_dict),word
                flag = "0"
            file_write.write(word + " " + flag + "\t")
        file_write.write("\n")
    file_write.close()


def analyse(standard_name, file_name):
    file_standard = open(standard_name, "r")
    file = open(file_name, "r")
    A = 0
    B = 0
    C = 0
    A1 = 0
    B1 = 0
    C1 = 0
    standards = []
    for line in file_standard:
        list = line.strip().split("\t")
        standard = []
        for item in list:
            item = item.split(" ")
            standard.append([item[0], item[1]])
        standards.append(standard)

    file_standard.close()

    for index, line in enumerate(file):
        list = line.strip().split("\t")

        standard_flag = "0"
        for item in standards[index]:
            if item[1] == "1":
                standard_flag = "1"
                break

        item_flag = "0"
        for index2, item in enumerate(list):
            item = item.split(" ")
            if item[1] == "1":
                item_flag = "1"
                break

        if standard_flag == "1" and item_flag == "1":
            A += 1
        elif standard_flag == "1" and item_flag == "0":
            C += 1
        elif standard_flag == "0" and item_flag == "1":
            B += 1

        if len(standards[index]) == len(list):
            for index2, item in enumerate(list):
                standard_flag = standards[index][index2][1]
                item = item.split(" ")
                item_flag = item[1]
                if standard_flag == "1" and item_flag == "1":
                    A1 += 1
                elif standard_flag == "1" and item_flag == "0":
                    C1 += 1
                elif standard_flag == "0" and item_flag == "1":
                    B1 += 1





    # print A,B,C
    recall = A * 1.0 / (A + C)
    precesion = A * 1.0 / (A + B)
    F = recall * precesion * 2 / (recall + precesion)

    print "recall:", recall, "precesion:", precesion, "F:", F
    recall = A1 * 1.0 / (A1 + C1)
    precesion = A * 1.0 / (A1 + B1)
    F = recall * precesion * 2 / (recall + precesion)
    print "recall:", recall, "precesion:", precesion, "F:", F


if __name__ == '__main__':
    init_dict("dict.txt")

    list = random.sample(range(0, 1600), 500)
    yuliao = []
    standard = []
    with open("yuliao.txt", "r") as f:
        yuliao = f.readlines()
    with open("standard.txt", "r") as ff:
        standard = ff.readlines()

    with open("yuliao1.txt", "w") as f0:
        with open("standard1.txt", "w") as f1:
            for item in list:
                f0.write(yuliao[item])
                f1.write(standard[item])
                standard[item] = ""

    with open("train.txt", "w") as f:
        for item in standard:
            if item:
                f.write(item)

    wc("yuliao1.txt")
    analyse("standard1.txt", "wc.txt")

    dp("yuliao1.txt")
    analyse("standard1.txt", "dp.txt")

    dp_word("yuliao1.txt")
    analyse("standard1.txt", "dp.txt")

    crf.crf_learn("train.txt")
    crf.crf("yuliao1.txt")
    analyse("standard1.txt", "crf.txt")


