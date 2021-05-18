#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''
flight.py
flight module
'''

from copy import deepcopy

class Flight(object):

    def __init__(self, position):
        self._position = position

    def get_position(self):
        return deepcopy(self._position)
