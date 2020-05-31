#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal
import time
import sys
import math

import numpy as np

from cyber_py3 import cyber

from modules.planning.proto.planning_pb2 import Trajectory
from modules.control.proto.chassis_pb2 import Chassis
from modules.planning.proto.planning_pb2 import Point
from modules.control.proto.control_pb2 import Control_Command
from modules.control.proto.control_pb2 import Control_Reference

sys.path.append("../")


class Control(object):

    def __init__(self, node):
        self.node = node
        self.speed = 0
        self.target_speed = 0
        self.lateral_error = 0
        self.cmd = Control_Command()
        self.trajectory = Trajectory()
        self.node.create_reader("/chassis", Chassis, self.chassiscallback)
        self.node.create_reader("/control_reference",
                                Control_Reference, self.speedrefcallback)
        self.node.create_reader(
            "/planning/dwa_trajectory", Trajectory, self.trajectorycallback)
        self.writer = self.node.create_writer("/control", Control_Command)

        signal.signal(signal.SIGINT, self.sigint_handler)
        signal.signal(signal.SIGHUP, self.sigint_handler)
        signal.signal(signal.SIGTERM, self.sigint_handler)
        self.is_sigint_up = False
        while True:
            try:
                time.sleep(0.05)
                self.lateral_controller(self.trajectory, self.lateral_error)
                self.longitude_controller(self.target_speed, self.speed)
                self.writer.write(self.cmd)
                if self.is_sigint_up:
                    print("Exit")
                    self.is_sigint_up = False
                    return
            except Exception:
                break

    def chassiscallback(self, data):
        self.speed = data.speed

    def sigint_handler(self, signum, frame):
            #global is_sigint_up
        self.is_sigint_up = True
        print("catched interrupt signal!")

    def speedrefcallback(self, data):
        self.target_speed = data.vehicle_speed

    def trajectorycallback(self, data):
        self.trajectory = data
        number = len(data.point)
        if (number > 0):
            self.lateral_error = math.sqrt(data.point[0].x * data.point[0].x +
                                      data.point[0].y * data.point[0].y) * data.point[0].x / abs(data.point[0].x)

    def lateral_controller(self, trajectory, lateral_error):
        # TODO  you should calculate steerangle here
        self.cmd.steer_angle = 0
        pass

    def longitude_controller(self, target_speed, speed_now):
        # TODO  you should calculate throttle here
        self.cmd.throttle = 0
        pass


if __name__ == '__main__':
    cyber.init()
    exercise_node = cyber.Node("control_node")
    exercise = Control(exercise_node)
