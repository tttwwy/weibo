__author__ = 'Administrator'
# coding=utf-8
import multiprocessing
import time


def worker(num):
    print "worker:", num
    time.sleep(2)
    return


jobs = []
for i in range(10):
    p = multiprocessing.Process(target=worker, args=(i,))
    jobs.append(p)
    p.start()
    p.join()
