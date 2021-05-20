#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
main.py
manage module
'''

from copy import deepcopy
from flight import Flight
from core import SaPhase1, SaPhase2, SaPhaseAll
import math

import json

import os

CUR_DIR=os.path.abspath(os.path.dirname(__file__)) + "/"

NUM_OF_REQUEST = 0
NUM_OF_POINT = 30
NUM_OF_FLIGHT = 5
SPEED_OF_FLIGHT = 15
INTEL = True

MAX_WEIGHT = 1000000

POINT = {}
DIST = []
FLIGHT = {}

MISSIONS = []

MISSION_A = []
MISSION_B = []
TODO_LIST = []
POSITION = []
CURRENT_COST = []

WEIGHT_LOAD = 0.5

def initialize_point():
    global POINT
    f = open(CUR_DIR+"data/point.txt")
    lines = f.read().splitlines()
    for line in lines:
        temp = line.split(" ")
        POINT[int(temp[0])] = [float(temp[1]), float(temp[2])]
    f.close()

def initialize_dist():
    global DIST
    DIST = [[float(0) for i in range(NUM_OF_POINT)] for j in range(NUM_OF_POINT)]
    f = open(CUR_DIR+"data/route.txt")
    lines = f.read().splitlines()
    for line in lines:
        temp = line.split(" ")
        DIST[int(temp[0])][int(temp[1])] = float(temp[2])
        DIST[int(temp[1])][int(temp[0])] = float(temp[2])
    f.close()

def load_file():
    initialize_point()
    initialize_dist()

def init_center():
    global MISSION_A
    global MISSION_B
    global TODO_LIST
    global POSITION
    global CURRENT_COST
    global FLIGHT
    MISSION_A = []
    MISSION_B = []
    TODO_LIST = []
    POSITION = []
    CURRENT_COST = []
    FLIGHT = {}
    for i in range(NUM_OF_FLIGHT):
        FLIGHT[i] = Flight(deepcopy([118958877.0, 32114745.0]))
        POSITION.append([118958877.0, 32114745.0])
        CURRENT_COST.append(0.0)
        MISSION_A.append([])
        MISSION_B.append([])
        TODO_LIST.append([])

def generate_distance(position):
    cost = {}
    len_of_content = NUM_OF_POINT + 1
    for i in range(NUM_OF_FLIGHT):
        content = [[float(0) for j in range(len_of_content)] for k in range(len_of_content)]
        for j in range(1, len_of_content):
            c = math.sqrt(pow(position[i][0] - POINT[j-1][0], 2) + pow(position[i][1] - POINT[j-1][1], 2)) / SPEED_OF_FLIGHT
            content[0][j] = c
            content[j][0] = c
        for j in range(1, len_of_content):
            for k in range(j+1, len_of_content):
                c = DIST[j-1][k-1] / SPEED_OF_FLIGHT
                content[j][k] = c
                content[k][j] = c
        cost[i] = content
    return deepcopy(cost)

def generate_cost_current(content, flight_id):
    if len(TODO_LIST[flight_id]) == 0:
        return 0.0
    else:
        time_all = 0
        cost_all = 0
        for i in range(len(TODO_LIST[flight_id])):
            point_id = TODO_LIST[flight_id][i]["point"]
            if i == 0:
                time_all += content[0][point_id + 1]
            else:
                time_all += content[TODO_LIST[flight_id][i - 1]["point"] + 1][point_id + 1]
            if "put" in TODO_LIST[flight_id][i]["todo"].keys():
                cost_all += time_all * len(TODO_LIST[flight_id][i]["todo"]["put"])
        return cost_all

def generate_route(a, b):
    route = []
    for i in range(len(a)):
        route.append(a[i][2])
    for i in range(len(b)):
        route.append(b[i][1])
    return deepcopy(list(set(route)))

def handle_each_mission(mission):

    for i in range(NUM_OF_FLIGHT):
        POSITION[i] = FLIGHT[i].get_position()
    cost = generate_distance(deepcopy(POSITION))

    current_cost = {}
    new_cost = {}
    delta_cost = {}
    flight_time = {}
    mission_b_temp = {}
    todo_list_temp = {}

    for i in range(NUM_OF_FLIGHT):

        current_cost[i] = generate_cost_current(deepcopy(cost[i]), i)

        b_temp = deepcopy(MISSION_B[i])
        b_temp.append(mission)
        a_temp = deepcopy(MISSION_A[i])

        route1 = generate_route(deepcopy(a_temp), deepcopy(b_temp))
        sa_phase1 = SaPhase1(deepcopy(a_temp), deepcopy(b_temp), deepcopy(cost[i]))
        """
        A + B' = route1 + todolist1 + A' + cost1 + time1
        """
        min_route1, cost_all1, time_all1, todo_list1, a_new = sa_phase1.min_cost(deepcopy(route1))

        route2 = generate_route(deepcopy(a_new), deepcopy([]))
        sa_phase2 = SaPhase2(deepcopy(a_new), deepcopy(cost[i]), min_route1[-1])
        """
        A' = route2 + todolist2 + cost2 + time2
        """
        min_route2, cost_all2, time_all2, todo_list2 = sa_phase2.min_cost(deepcopy(route2))

        todo_list = todo_list1 + todo_list2

        sa_phase_all = SaPhaseAll(deepcopy(a_temp), deepcopy(b_temp), deepcopy(cost[i]))
        """
        cost_new + todo_list_new = todo_list
        """
        cost_time_all, flight_time_all, todo_list_all = sa_phase_all.min_cost(deepcopy(todo_list))
        new_cost[i] = cost_time_all

        # print("{} | {}".format(current_cost[i], new_cost[i]))

        delta_cost[i] = (new_cost[i] - current_cost[i]) + WEIGHT_LOAD * current_cost[i]
        flight_time[i] = flight_time_all
        mission_b_temp[i] = deepcopy(b_temp)
        todo_list_temp[i] = deepcopy(todo_list_all)

    index = -1
    min_delta = MAX_WEIGHT

    for i in range(NUM_OF_FLIGHT):
        if delta_cost[i] < min_delta:
            index = i
            min_delta = delta_cost[i]

    MISSION_B[index] = deepcopy(mission_b_temp[index])
    TODO_LIST[index] = deepcopy(todo_list_temp[index])

    for i in range(NUM_OF_FLIGHT):
        CURRENT_COST[i] = generate_cost_current(deepcopy(cost[i]), i)
    # print(MISSION_A)
    # print(MISSION_B)
    # print(TODO_LIST)
    # print(CURRENT_COST)
    # print("\n\n")

def manage():
    init_center()
    for m in MISSIONS:
        handle_each_mission(deepcopy(m))

def solve():
    init_center()
    for m in MISSIONS:
        mission_id = m[0]
        sp = m[1]
        ep = m[2]
        flight_id = mission_id % NUM_OF_FLIGHT
        MISSION_B[flight_id].append(deepcopy(m))
        TODO_LIST[flight_id].append({"point": sp, "todo": {"get": [mission_id]}})
        TODO_LIST[flight_id].append({"point": ep, "todo": {"put": [mission_id]}})
    cost = generate_distance(deepcopy(POSITION))
    for i in range(NUM_OF_FLIGHT):
        CURRENT_COST[i] = generate_cost_current(deepcopy(cost[i]), i)

def handle(event, context):
    global MISSIONS
    global NUM_OF_FLIGHT
    global INTEL
    tmp = event['data']
    if type(tmp)==bytes: 
        tmp = json.loads(tmp)
    if type(tmp) != dict:
        return "Error"
    if "mission" in tmp:
        file_content = tmp['mission']
        MISSIONS = []
        lines = file_content.splitlines()
        for line in lines:
            tmp = line.split()
            MISSIONS.append([int(tmp[0]), int(tmp[1]), int(tmp[2])])
        print(MISSIONS)
        with open(CUR_DIR + "MISSION.json", "w") as f:
            f.write(json.dumps(MISSIONS))
        message = "success"
        response_body = json.dumps({"status": message})
        return response_body
    else:
        input_from_ui = tmp
        t = input_from_ui["type"]
        if t==0:
            print(input_from_ui)
            print("Optimization goal: {}".format(input_from_ui['select']))
            print("Intel algo: {}".format(input_from_ui['switch']))
            NUM_OF_FLIGHT = input_from_ui['slider']
            INTEL = input_from_ui['switch']
            with open(CUR_DIR + "NUM_OF_FLIGHT.txt", "w") as f:
                f.write(str(NUM_OF_FLIGHT))
            with open(CUR_DIR + "INTEL.txt", "w") as f:
                f.write(str(INTEL))
            response_body = json.dumps({"message": "save success"})
            return response_body
        if t==1:
            load_file()
            with open(CUR_DIR + "MISSION.json", "r") as f:
                content = f.read()
                MISSIONS = json.loads(content)
            with open(CUR_DIR + "NUM_OF_FLIGHT.txt", "r") as f:
                content = f.read()
                NUM_OF_FLIGHT =  int(content)
            with open(CUR_DIR + "INTEL.txt", "r") as f:
                content = f.read()
                if content == "True":
                    INTEL = True
                else:
                    INTEL = False
            # print("MISSIONS", MISSIONS)
            # print("NUM_OF_FLIGHT", NUM_OF_FLIGHT)
            # print("INTEL", INTEL)
            print("planning...")
            if INTEL:
                manage()
            else:
                solve()
            flight_mission = []
            for i in range(NUM_OF_FLIGHT):
                tmp = {}
                tmp["key"] = str(i)
                tmp["id"] = str(i)
                tmp["mission"] = ""
                for j in range(len(MISSION_B[i])):
                    tmp["mission"] += str(MISSION_B[i][j][0])
                    if j < len(MISSION_B[i]) - 1:
                        tmp["mission"] += " , "
                tmp["cost"] = "{:.2f}".format(CURRENT_COST[i])
                flight_mission.append(tmp)
            flight_todolist = []
            for i in range(NUM_OF_FLIGHT):
                tmp = {}
                tmp["key"] = str(i)
                tmp["id"] = str(i)
                tmp["list"] = ""
                for j in range(len(TODO_LIST[i])):
                    tmp["list"] += " -> " + str(TODO_LIST[i][j]["point"]) + " : "
                    tmp["list"] += "( "
                    if "put" in TODO_LIST[i][j]["todo"].keys():
                        tmp["list"] += "put : "
                        for k in range(len(TODO_LIST[i][j]["todo"]["put"])):
                            tmp["list"] += str(TODO_LIST[i][j]["todo"]["put"][k]) + " "
                    if "get" in TODO_LIST[i][j]["todo"].keys():
                        tmp["list"] += "get : "
                        for k in range(len(TODO_LIST[i][j]["todo"]["get"])):
                            tmp["list"] += str(TODO_LIST[i][j]["todo"]["get"][k]) + " "
                    tmp["list"] += ")"
                flight_todolist.append(tmp)
            response_body = json.dumps({"todo_list": TODO_LIST, "position": POSITION, "flight_mission": flight_mission, "flight_todolist": flight_todolist})
            return bytes(response_body, encoding='utf-8')
