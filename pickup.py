# coding=utf-8
import os
import Queue
import time
import logging
import multiprocessing
from langconv import *
import base
import rule


reload(sys)
sys.setdefaultencoding("utf-8")
__author__ = 'WangZhe'

logging.basicConfig(
    level=logging.DEBUG,
    format=' %(process)d: %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='yinshi.log',

    filemode='a'
)
workspace_dir = os.path.dirname(sys.argv[0] if len(sys.argv) < 4  else sys.argv[3])


class Pickup(base.Base):
    full_index = {}

    queue = Queue.PriorityQueue()
    key_words = (
    "吃".decode('utf-8'),
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
    "饱".decode('utf-8')
    )

    def pickup_file(self, file_name):
        logging.info("%s pickup begin" % (file_name))
        file = open(file_name, "r")
        file_write_name = os.path.join(workspace_dir,"temp", os.path.basename(file_name) + ".ban")
        if not os.path.exists(os.path.dirname(file_write_name)):
            os.makedirs(os.path.dirname(file_write_name))
        file_write = open(file_write_name, "w")
        self.full_index.clear()
        xml_index = 0
        for index, line in enumerate(file):
            id, content, time, location, sex = line.strip().split("\t\t")

            # bak = line.strip().decode('utf-8')
            # bak = content
            content = self.ban_rubbish(content.decode('utf-8'))
            if content == "":
                # print bak
                continue

            for item in self.split_sentence(content):
                for word in self.key_words:
                    if item.find(word) != -1:
                        item = Converter('zh-hans').convert(item)
                        file_write.write(item + "\n")
                        self.full_index[xml_index] = index
                        xml_index += 1
                        break

        file.close()
        file_write.close()
        logging.info("%s pickup end" % (file_write_name))
        return file_write_name


    # def rule_handle(self,nodes):
    #
    #     result = []
    #     for node in nodes:
    #         if node["relate"] == "VOB" \
    #                 and node["pos"].find("n") != -1 \
    #                 and (nodes[node["parent"]]["cont"] == "喝" or nodes[node["parent"]]["cont"] == "吃"):
    #             result.append([node["cont"],"1"])
    #         else:
    #             result.append([node["cont"],"0"])
    #
    #     return result


    def get_full_text(self, file_name, queue):
        logging.info("%s final begin" % (file_name))
        file = open(file_name, "r")

        if not queue.empty():
            index, word = queue.get()
            for cur_index, line in enumerate(file):
                while cur_index == index:
                    yield (word, line.strip())
                    if queue.empty():
                        file.close()
                        return
                    else:
                        index, word = queue.get()
                if cur_index > index:
                    if queue.empty():
                        break
                    else:
                        index, word = queue.get()
        file.close()


    def worker(self, file):

        file_name = self.pickup_file(file)
        file_name = self.word_split_file(file_name)
        file_name = self.pos_file(file_name)
        file_name = self.dp_file(file_name)
        # queue = Queue.PriorityQueue()
        # rule_handle = rule.Rule()
        # rule_handle.load_model("rule_model.txt")
        #
        # for index, nodes in enumerate(self.xml_read(file_name)):
        #     foods = rule_handle.test(nodes)
        #     for food in foods:
        #         print food, self.full_index[index]
        #         queue.put((self.full_index[index], food))
        #
        # with open(workspace_dir.join("temp", os.path.basename(file) + ".result"), "w") as f:
        #     for word, line in self.get_full_text(file, queue):
        #         f.write("{0}\t\t{1}\n".format(word, line))


if __name__ == '__main__':

    # logging.info("begin:%s"%(sys.argv[1]))
    pickup = Pickup()

    start = time.time()

    pickup.add_dict(os.path.join(os.path.dirname(sys.argv[0]),"dict/dict.txt") )
    pickup.add_dict(os.path.join(os.path.dirname(sys.argv[0]),"dict/ws_dict.txt") )




    # pickup.worker("yuliao.txt_0.ban.ws.pos.dp")


    sum_line = 0
    with open(sys.argv[1], "r") as file:
        for line in file:
            sum_line += 1

    thread_num = int(sys.argv[2])
    offset = int((sum_line + thread_num - 1) / thread_num)

    logging.info("line:%d offset:%d" % (sum_line, offset))
    file = open(sys.argv[1], "r")

    # offset = 100000
    logging.info("thread_num:%d" % (thread_num))
    num = 0
    f = open(sys.argv[1] + "_" + str(num), "w")
    file_list = []
    for index, line in enumerate(file):
        if index % offset == 0:
            f.close()
            f = open(sys.argv[1] + "_" + str(num), "w")
            file_list.append(sys.argv[1] + "_" + str(num))
            num += 1
        f.write(line)
    f.close()

    jobs = []
    for index, file in enumerate(file_list):
        p = multiprocessing.Process(target=pickup.worker, args=(file,))
        jobs.append(p)
        p.start()

    for job in jobs:
        job.join()


    file_write_name = os.path.join(workspace_dir,"result", os.path.basename(sys.argv[1]) + ".result")
    os.makedirs(os.path.dirname(file_write_name))
    file_write = open(file_write_name, "w")
    for file_name in file_list:
        file_read = open(os.path.join(workspace_dir,"temp", os.path.basename(file_name) + ".result"), "r")
        for line in file_read:
            file_write.write(line)
        file_read.close()
    file_write.close()

    end = time.time()
    logging.info("end process \n time cost:%d" % (end - start))

