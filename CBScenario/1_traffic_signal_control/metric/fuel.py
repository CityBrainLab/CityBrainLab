from . import BaseMetric
import numpy as np


class FuelMetric(BaseMetric):
    """
    Calculate average travel time of all vehicles.
    For each vehicle, travel time measures time between it entering and leaving the roadnet.
    """

    def __init__(self, world):
        self.world = world
        self.world.subscribe(["vehicles", "time", "lane_vehicles"])
        self.vehicle_route = {}
        self.vehicle_fuel = {}

        # calculate road lengths
        self.road_length = {}
        for road_id, road in self.world.all_roads.items():
            self.road_length[road_id] = road.length

    def reset(self):
        self.vehicle_route = {}
        self.vehicle_fuel = {}

    def cal_fuel(self, routes):
        distance = 0
        ratio = 71.294 / (68593.74 - 0)
        for road in routes:
            distance += self.road_length[road]

        return distance * ratio * 2.4

    def update(self, done=False):
        vehicles = self.world.get_info("vehicles")
        current_time = self.world.get_info("time")
        lane_vehicles = self.world.get_info("lane_vehicles")

        dic_vehicle_lane = {}
        for lane_id, lane in lane_vehicles.items():
            for vehicle in lane:
                dic_vehicle_lane[vehicle] = self._get_road_for_lane(lane_id)

        for vehicle in vehicles:
            if not vehicle in self.vehicle_route:
                if vehicle in dic_vehicle_lane:
                    self.vehicle_route[vehicle] = [dic_vehicle_lane[vehicle]]
                else:
                    continue
        for vehicle in list(self.vehicle_route):
            if vehicle in dic_vehicle_lane:
                if self.vehicle_route[vehicle][-1] != dic_vehicle_lane[vehicle]:
                    self.vehicle_route[vehicle].append(dic_vehicle_lane[vehicle])

        for vehicle in self.vehicle_route:
            self.vehicle_fuel[vehicle] = self.cal_fuel(self.vehicle_route[vehicle])

        if done:
            print("eveluated vehicles:", len(self.vehicle_fuel))

        return (
            np.mean(list(self.vehicle_fuel.values())) if len(self.vehicle_fuel) else 0
        )

    def _get_road_for_lane(self, lane):
        return int(int(lane)/100)

