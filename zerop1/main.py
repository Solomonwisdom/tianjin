#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import os
import json

CUR_DIR=os.path.abspath(os.path.dirname(__file__)) + "/"
f = open(CUR_DIR + "route.txt")
lines = f.read().splitlines()
f.close()

cost = [[0.0 for i in range(30)] for j in range(30)]

for line in lines:
    line = line.split()
    cost[int(line[0])][int(line[1])] = float(line[2])
    cost[int(line[1])][int(line[0])] = float(line[2])

# 这里的cost是地图的代价矩阵，从文件读入


# 服务的含义是给定一个无人机访问路径，以及其续行里程，判断其能否完成任务
# 传递的参数是访问路径tdl，续行里程left，需要调用你那里已经保存的cost
# test则是需要封装的服务
def test(tdl, left):
    for i in range(len(tdl)):
        if i > 0:
            left -= cost[tdl[i-1]][tdl[i]]
        if left < 0:
            return False
    return True

# 比如在此tdl的情形下，left为20000则为Fasle，left为30000则为True

def handle(event, context):
    data = event['data']
    if type(data)==bytes: 
        data = json.loads(data)
    if type(data) != dict:
        return "error"
    tdl = data["tdl"]
    left = data["left"]
    if test(tdl, left):
        return "true"
    else:
        return "false"

