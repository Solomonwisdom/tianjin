#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
core.py
manage core module
'''

from copy import deepcopy
import random
import math

INITIAL_TEMPERATURE_1 = 120
FINAL_TEMPERATURE_1 = 0.001

INITIAL_TEMPERATURE_2 = 1
FINAL_TEMPERATURE_2 = 0.001
REJECT_NUM_2 = 2
ITERATION_NUM_2 = 4

INITIAL_TEMPERATURE_ALL = 120
FINAL_TEMPERATURE_ALL = 0.001

MAX_W = 100000000

class SaPhase1(object):

    def __init__(self, mission_a, mission_b, cost):
        # A
        self._a = mission_a
        # B
        self._b = mission_b
        # current flight cost matrix
        self._cost = cost

    def _imitate(self, route):
        a = deepcopy(self._a)
        b = deepcopy(self._b)
        # route time
        time_all = 0
        # mission time
        cost_all = 0
        # [...[td,td...]...] td = {id:point_id,td:{get:[i,i...],put:[i,i...]}} i = mission_id
        todo_list = []
        for i in range(len(route)):
            point_id = route[i]
            if i == 0:
                # position now to point 0
                time_all += self._cost[0][point_id + 1]
            else:
                # point i-1 to point i
                time_all += self._cost[route[i - 1] + 1][point_id + 1]
            todo_now = {"point": point_id, "todo": {}}
            # to store the missions that are finished
            finish = []
            # traverse A to find missions to finish
            for j in range(len(a)):
                # check the end point
                if a[j][2] == point_id:
                    finish.append(a[j])
                    if "put" not in todo_now["todo"].keys():
                        todo_now["todo"]["put"] = []
                    # add the finished mission id to the list
                    todo_now["todo"]["put"].append(a[j][0])
                    # mission finished and add the cost
                    cost_all += time_all
            for j in range(len(finish)):
                # remove it from a
                a.remove(finish[j])
            # to store the missions that are started
            start = []
            # traverse B to find missions to start
            for j in range(len(b)):
                # check the start point
                if b[j][1] == point_id:
                    start.append(b[j])
                    if "get" not in todo_now["todo"].keys():
                        todo_now["todo"]["get"] = []
                    # add the started mission id to the list
                    todo_now["todo"]["get"].append(b[j][0])
            for j in range(len(start)):
                # remove it from b
                b.remove(start[j])
                # add it to a
                a.append(start[j])
            # append the todo_now to the todo_list
            todo_list.append(todo_now)
        # add the cost of those missions that have not finished
        cost_all += len(a) * time_all
        return cost_all, time_all, deepcopy(todo_list), deepcopy(a)

    def min_cost(self, route):
        # route does not need to change and it only needs to imitate
        if len(route) == 1:
            cost_all, time_all, todo_list, a_new = self._imitate(deepcopy(route))
            return deepcopy(route), cost_all, time_all, deepcopy(todo_list), deepcopy(a_new)

        cost_all, time_all, todo_list, a_new = self._imitate(deepcopy(route))
        current_temperature = INITIAL_TEMPERATURE_1
        # short route can be stable and does not need a high temperature
        if len(route) < 20:
            current_temperature = current_temperature * len(route) / 20

        cal = 0
        l = len(route)
        if l <= 10:
            reject_num = l * l
        elif 10 < l and l <= 20:
            reject_num = 100 + (l - 10) * (l - 10)
        else:
            reject_num = 200
        iteration_num = reject_num * 2

        while current_temperature > FINAL_TEMPERATURE_1:
            # temperature loop
            count_reject = 0
            count_iteration = 0
            while count_reject < reject_num and count_iteration < iteration_num:
                # reject loop
                point1 = 0
                point2 = 0
                judge = 0
                while point1 == point2 and judge < 5:
                    # point1!=point2
                    point1 = random.randint(0, len(route) - 1)
                    point2 = random.randint(0, len(route) - 1)
                    judge += 1
                temp = route[point1]
                # swap and temp = point1
                route[point1] = route[point2]
                route[point2] = temp
                cost_all_new, time_all_new, todo_list_new, a_new_new = self._imitate(deepcopy(route))
                cal += 1
                cost_delta = cost_all_new - cost_all
                # smaller
                if cost_delta < 0:
                    # accept
                    cost_all = cost_all_new
                    time_all = time_all_new
                    todo_list = deepcopy(todo_list_new)
                    a_new = deepcopy(a_new_new)
                else:
                    # larger
                    accept_rate = math.exp(-cost_delta / current_temperature)
                    rand = random.random()
                    if accept_rate > rand:
                        # accept
                        cost_all = cost_all_new
                        time_all = time_all_new
                        todo_list = deepcopy(todo_list_new)
                        a_new = deepcopy(a_new_new)
                    else:
                        # reject
                        route[point2] = route[point1]
                        route[point1] = temp
                        count_reject += 1
                count_iteration += 1
            # change the temperature
            current_temperature *= 0.2

        print(cal)

        return deepcopy(route), cost_all, time_all, deepcopy(todo_list), deepcopy(a_new)


class SaPhase2(object):

    def __init__(self, mission_a, cost, current_id):
        # new A
        self._a = mission_a
        # current flight cost matrix
        self._cost = cost
        # current position id
        self._current_id = current_id

    def _imitate(self, route):
        a = deepcopy(self._a)
        # route time
        time_all = 0
        # mission time
        cost_all = 0
        # [...[td,td...]...] td = {id:point_id,td:{get:[i,i...],put:[i,i...]}} i = mission_id
        todo_list = []
        for i in range(len(route)):
            point_id = route[i]
            if i == 0:
                # current position id to point 0
                time_all += self._cost[self._current_id + 1][point_id + 1]
            else:
                # point i-1 to point i
                time_all += self._cost[route[i - 1] + 1][point_id + 1]
            todo_now = {"point": point_id, "todo": {}}
            # to store the missions that are finished
            finish = []
            # traverse A to find missions to finish
            for j in range(len(a)):
                # check the end point
                if a[j][2] == point_id:
                    finish.append(a[j])
                    if "put" not in todo_now["todo"].keys():
                        todo_now["todo"]["put"] = []
                    # add the finished mission id to the list
                    todo_now["todo"]["put"].append(a[j][0])
                    # mission finished and add the cost
                    cost_all += time_all
            for j in range(len(finish)):
                # remove it from a
                a.remove(finish[j])
            # append the todo_now to the todo_list
            todo_list.append(todo_now)
        assert (len(a) == 0)
        return cost_all, time_all, deepcopy(todo_list)

    def min_cost(self, route):
        # route = []
        if len(route) == 0:
            todo_list = []
            return deepcopy(route), 0, 0, deepcopy(todo_list)
        # route does not need to change and it only needs to imitate
        if len(route) == 1:
            cost_all, time_all, todo_list = self._imitate(deepcopy(route))
            return deepcopy(route), cost_all, time_all, deepcopy(todo_list)

        cost_all, time_all, todo_list = self._imitate(deepcopy(route))
        current_temperature = INITIAL_TEMPERATURE_2
        # short route can be stable and does not need a high temperature
        cal = 0
        if len(route) < 20:
            current_temperature = current_temperature * len(route) / 20

        while current_temperature > FINAL_TEMPERATURE_2:
            # temperature loop
            count_reject = 0
            count_iteration = 0
            while count_reject < REJECT_NUM_2 and count_iteration < ITERATION_NUM_2:
                # reject loop
                point1 = 0
                point2 = 0
                judge = 0
                while point1 == point2 and judge < 5:
                    # point1!=point2
                    point1 = random.randint(0, len(route) - 1)
                    point2 = random.randint(0, len(route) - 1)
                    judge += 1
                temp = route[point1]
                # swap and temp = point1
                route[point1] = route[point2]
                route[point2] = temp
                cost_all_new, time_all_new, todo_list_new = self._imitate(deepcopy(route))
                cal += 1
                cost_delta = cost_all_new - cost_all
                # smaller
                if cost_delta < 0:
                    # accept
                    cost_all = cost_all_new
                    time_all = time_all_new
                    todo_list = deepcopy(todo_list_new)
                else:
                    # larger
                    accept_rate = math.exp(-cost_delta / current_temperature)
                    rand = random.random()
                    if accept_rate > rand:
                        # accept
                        cost_all = cost_all_new
                        time_all = time_all_new
                        todo_list = deepcopy(todo_list_new)
                    else:
                        # reject
                        route[point2] = route[point1]
                        route[point1] = temp
                        count_reject += 1
                count_iteration += 1
            # change the temperature
            current_temperature *= 0.1

        print(cal)

        return deepcopy(route), cost_all, time_all, deepcopy(todo_list)


class SaPhaseAll(object):

    def __init__(self, mission_a, mission_b, cost):
        # A
        self._a = mission_a
        # B
        self._b = mission_b
        # current flight cost matrix
        self._cost = cost

    def _imitate(self, todo_list):
        # route time
        time_all = 0
        # mission time
        cost_all = 0
        # calculate
        for i in range(len(todo_list)):
            point_id = todo_list[i]["point"]
            if i == 0:
                # current position to point 0
                time_all += self._cost[0][point_id + 1]
            else:
                # point i-1 to point i
                time_all += self._cost[todo_list[i - 1]["point"] + 1][point_id + 1]
            # cost += flight_time * num_of_mission(finished now)
            if "put" in todo_list[i]["todo"].keys():
                cost_all += time_all * len(todo_list[i]["todo"]["put"])
        # check to validate
        a = deepcopy(self._a)
        b = deepcopy(self._b)
        for i in range(len(todo_list)):
            # find missions finished
            if "put" in todo_list[i]["todo"].keys():
                # to store the missions have been finished
                finish = []
                for j in range(len(a)):
                    if a[j][0] in todo_list[i]["todo"]["put"]:
                        finish.append(a[j])
                # remove the missions from A
                for j in range(len(finish)):
                    a.remove(finish[j])
            # find missions started
            if "get" in todo_list[i]["todo"].keys():
                # to store the missions have been started
                start = []
                for j in range(len(b)):
                    if b[j][0] in todo_list[i]["todo"]["get"]:
                        start.append(b[j])
                # remove the missions from B and add them to A
                for j in range(len(start)):
                    b.remove(start[j])
                    a.append(start[j])
        # check
        if len(a) > 0:
            return MAX_W, time_all
        return cost_all, time_all

    def min_cost(self, todo_list):
        # todo_list = []
        if len(todo_list) == 0:
            return 0, 0, deepcopy(todo_list)
        # todo_list does not need to change and it only needs to imitate
        if len(todo_list) == 1:
            cost_all, time_all = self._imitate(deepcopy(todo_list))
            return cost_all, time_all, deepcopy(todo_list)

        cost_all, time_all = self._imitate(deepcopy(todo_list))
        current_temperature = INITIAL_TEMPERATURE_ALL

        cal = 0
        l = len(todo_list)
        if l <= 10:
            reject_num = l * l
        elif 10 < l and l <= 20:
            reject_num = 100 + (l - 10) * (l - 10)
        else:
            reject_num = 200
        iteration_num = reject_num * 2

        while current_temperature > FINAL_TEMPERATURE_ALL:
            # temperature loop
            count_reject = 0
            count_iteration = 0
            while count_reject < reject_num and count_iteration < iteration_num:
                # reject loop
                point1 = 0
                point2 = 0
                judge = 0
                while point1 == point2 and judge < 5:
                    # point1!=point2
                    point1 = random.randint(0, len(todo_list) - 1)
                    point2 = random.randint(0, len(todo_list) - 1)
                    judge += 1
                temp = deepcopy(todo_list[point1])
                # swap and temp = point1
                todo_list[point1] = deepcopy(todo_list[point2])
                todo_list[point2] = deepcopy(temp)
                cost_all_new, time_all_new = self._imitate(deepcopy(todo_list))
                cal += 1
                if cost_all_new == MAX_W:
                    # reject
                    todo_list[point2] = deepcopy(todo_list[point1])
                    todo_list[point1] = deepcopy(temp)
                    count_reject += 1
                else:
                    cost_delta = cost_all_new - cost_all
                    # smaller
                    if cost_delta < 0:
                        # accept
                        cost_all = cost_all_new
                        time_all = time_all_new
                    else:
                        # larger
                        accept_rate = math.exp(-cost_delta / current_temperature)
                        rand = random.random()
                        if accept_rate > rand:
                            # accept
                            cost_all = cost_all_new
                            time_all = time_all_new
                        else:
                            # reject
                            todo_list[point2] = deepcopy(todo_list[point1])
                            todo_list[point1] = deepcopy(temp)
                            count_reject += 1
                count_iteration += 1
            # change the temperature
            if current_temperature > 60:
                current_temperature *= 0.8
            elif current_temperature > 6:
                current_temperature *= 0.5
            else:
                current_temperature *= 0.2

        print(cal)

        return cost_all, time_all, deepcopy(todo_list)
