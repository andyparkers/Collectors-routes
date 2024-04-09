import database as db
import random

import geoapi
import utility
import queue
import folium
import geoapi as gp
import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.distances import great_circle_distance_matrix


MOSCOW_RECTANGLE_BOUNDARIES = [[55.842213, 37.485103], [55.842213, 37.781673],
                               [55.651697, 37.485103], [55.651697, 37.781673]]


MOSCOW_COLLECTORS_START_POINTS = [
    [
        round((MOSCOW_RECTANGLE_BOUNDARIES[0][0] + MOSCOW_RECTANGLE_BOUNDARIES[3][0] / 6) / (1 + 1 / 6), 6),
        round((MOSCOW_RECTANGLE_BOUNDARIES[0][1] + MOSCOW_RECTANGLE_BOUNDARIES[3][1] / 6) / (1 + 1 / 6), 6)
    ],
    [
        round((MOSCOW_RECTANGLE_BOUNDARIES[1][0] + MOSCOW_RECTANGLE_BOUNDARIES[2][0] / 6) / (1 + 1 / 6), 6),
        round((MOSCOW_RECTANGLE_BOUNDARIES[1][1] + MOSCOW_RECTANGLE_BOUNDARIES[2][1] / 6) / (1 + 1 / 6), 6)
    ],
    [
        round((MOSCOW_RECTANGLE_BOUNDARIES[0][0] + MOSCOW_RECTANGLE_BOUNDARIES[2][0]) / 2, 6),
        round((MOSCOW_RECTANGLE_BOUNDARIES[0][1] + MOSCOW_RECTANGLE_BOUNDARIES[1][1]) / 2, 6)
    ],
    [
        round((MOSCOW_RECTANGLE_BOUNDARIES[1][0] + MOSCOW_RECTANGLE_BOUNDARIES[2][0] * 5) / 6, 6),
        round((MOSCOW_RECTANGLE_BOUNDARIES[1][1] + MOSCOW_RECTANGLE_BOUNDARIES[2][1] * 5) / 6, 6)
    ],
    [
        round((MOSCOW_RECTANGLE_BOUNDARIES[0][0] + MOSCOW_RECTANGLE_BOUNDARIES[3][0] * 5) / 6, 6),
        round((MOSCOW_RECTANGLE_BOUNDARIES[0][1] + MOSCOW_RECTANGLE_BOUNDARIES[3][1] * 5) / 6, 6)
    ]
]


class Atm:
    def __init__(self, coordinates, uid):
        self.__uid = uid
        self.__longitude = coordinates[0]
        self.__latitude = coordinates[1]
        self.__banknotes_d_x = 25
        self.__banknotes_m_x = 235
        self.__input_capacity_banknotes = 8000
        self.__output_capacity_banknotes = 8000
        self.__current_input_volume = random.gauss(self.__banknotes_m_x,
                                                   self.__banknotes_d_x)
        self.__current_output_volume = random.gauss(self.__output_capacity_banknotes - self.__banknotes_m_x,
                                                    self.__banknotes_d_x)

    def set_current_output_volume(self, new_output_volume: int):
        db.update_value_in_db("atms_data", "output_capacity", new_output_volume, "atm_id", self.__uid)

    def set_current_input_volume(self, new_input_volume: int):
        db.update_value_in_db("atms_data", "input_capacity", new_input_volume, "atm_id", self.__uid)

    def refresh_atm(self):
        self.set_current_input_volume(0)
        self.set_current_output_volume(self.__output_capacity_banknotes)

    def add_to_current_input(self, value: int, is_commit=False):
        db_input_value = db.get_column_row_from_db("atms_data", "input_capacity", "atm_id", self.__uid)
        db_atm_capacity = db.get_column_row_from_db("atms_data", "capacity", "atm_id", self.__uid)
        if db_input_value + value <= db_atm_capacity:
            self.set_current_input_volume(db_input_value + value)
        else:
            self.set_current_input_volume(db_atm_capacity)
        if is_commit:
            db.connection.commit()

    def add_to_current_output(self, value: int, is_commit=False):
        db_output_value = db.get_column_row_from_db("atms_data", "output_capacity", "atm_id", self.__uid)
        if db_output_value - value >= 0:
            self.set_current_output_volume(db_output_value - value)
        else:
            self.set_current_output_volume(0)
        if is_commit:
            db.connection.commit()

    def get_input_capacity_banknotes(self):
        return db.get_column_row_from_db("atms_data", "capacity", "atm_id", self.__uid)

    def get_output_capacity_banknotes(self):
        return db.get_column_row_from_db("atms_data", "capacity", "atm_id", self.__uid)

    def get_longitude(self):
        return db.get_column_row_from_db("atms_data", "longitude", "atm_id", self.__uid)

    def get_latitude(self):
        return db.get_column_row_from_db("atms_data", "latitude", "atm_id", self.__uid)

    def get_uid(self):
        return self.__uid

    def set_longitude(self, longitude):
        self.__longitude = longitude

    def set_latitude(self, latitude):
        self.__latitude = latitude

    def get_coordinates(self) -> list:
        return [self.get_longitude(), self.get_latitude()]  # change to using DB data

    def get_current_input_volume(self):
        return db.get_column_row_from_db("atms_data", "input_capacity", "atm_id", self.__uid)

    def get_current_output_volume(self):
        return db.get_column_row_from_db("atms_data", "output_capacity", "atm_id", self.__uid)

    def get_mx(self):
        return db.get_column_row_from_db("atms_data", "m_x", "atm_id", self.__uid)

    def get_dx(self):
        return db.get_column_row_from_db("atms_data", "d_x", "atm_id", self.__uid)


class MoscowCollectors:
    def __init__(self, collectors_list: list):
        self.__collectors_list = collectors_list

    def get_collectors_list(self) -> list:
        return self.__collectors_list


class MoscowAtms:
    def __init__(self):
        self.atms_queue = queue.Queue()
        self.screenshot_counter = 1
        self.__uid_to_atm = dict()
        self.__atms_data = []
        self.__max_input_amount = 8000
        self.__max_output_amount = 0
        self.__max_atms_in_queue = 50

    def get_atms(self):
        return self.__atms_data

    def add_atm(self, atm):
        self.__atms_data.append(atm)

    def get_queue(self) -> queue:
        return self.atms_queue

    def fill_queue(self, number):
        unique_atms = set()
        self.__atms_data.sort(key=lambda x: x.get_current_input_volume(), reverse=True)  # reverse for input

        k = 0
        while self.atms_queue.qsize() != (number // 2):
            if self.__atms_data[k] not in unique_atms:
                unique_atms.add(self.__atms_data[k])
                self.atms_queue.put(self.__atms_data[k])
            k += 1

        self.__atms_data.sort(key=lambda x: x.get_current_output_volume(), reverse=False)  # in order for output

        k = 0
        while self.atms_queue.qsize() != number:
            if self.__atms_data[k] not in unique_atms:
                unique_atms.add(self.__atms_data[k])
                self.atms_queue.put(self.__atms_data[k])
            k += 1

    def get_latest_atm_from_queue(self):
        if not self.atms_queue.empty():
            return self.atms_queue.get()
        return False

    def simulate_one_day(self):
        for atm in self.__atms_data:
            current_input = int(random.gauss(atm.get_mx(), atm.get_dx()))
            current_output = int(random.gauss(atm.get_mx(), atm.get_dx()))
            atm.add_to_current_input(current_input)
            atm.add_to_current_output(current_output)
        db.connection.commit()
        self.fill_queue(self.__max_atms_in_queue)

    def refresh_queued_atms(self):
        for _ in range(self.__max_atms_in_queue):
            if not self.atms_queue.empty():
                self.atms_queue.get().refresh_atm()

    def get_first_n_sorted_atms(self, n):
        self.__atms_data.sort(key=lambda x: x.get_current_input_volume(), reverse=True)
        return self.__atms_data[:n]

    def get_atm(self, uid):
        return self.__atms_data[uid]

    def distribute_atms_to_collectors(self, collectors: list):
        counter = 0
        collectors_to_assigned_atms = dict([])
        while True:
            dict_queue = dict()
            new_atm = self.get_latest_atm_from_queue()
            if new_atm is False:
                break
            for collector in collectors:
                dict_queue[utility.get_distance_between_geocoord(list(new_atm.get_coordinates()),
                                                                 list(collector.get_coordinates()))] = collector
            valid_collector = dict_queue[min(dict_queue.keys())]
            if valid_collector not in collectors_to_assigned_atms:
                collectors_to_assigned_atms[valid_collector] = []
            collectors_to_assigned_atms[valid_collector].append([new_atm, min(dict_queue.keys())])
            counter += 1

        excess_atms = []

        for collector, atms_array in collectors_to_assigned_atms.items():
            if len(atms_array) > self.__max_atms_in_queue // len(collectors_to_assigned_atms) + 0:
                atms_array = sorted(atms_array, key=lambda x: x[1], reverse=True)
                append_counter = 0
                append_limit = len(atms_array) - (self.__max_atms_in_queue // len(collectors) + 0)
                for atm in atms_array:
                    if append_counter == append_limit:
                        break
                    excess_atms.append(atm)
                    collectors_to_assigned_atms[collector].remove(atm)
                    append_counter += 1

        for extra_atm in excess_atms:
            dict_queue = dict()
            for collector in collectors:
                dict_queue[utility.get_distance_between_geocoord(extra_atm[0].get_coordinates(),
                                                                 collector.get_coordinates())] = collector
            if len(collectors_to_assigned_atms[dict_queue[min(dict_queue.keys())]]) >= self.__max_atms_in_queue // len(
                    collectors) + 3:
                for _ in range(len(collectors) - 1):
                    dict_queue.pop(min(dict_queue.keys()))
                    if len(collectors_to_assigned_atms[dict_queue[min(dict_queue.keys())]]) < self.__max_atms_in_queue // len(
                            collectors) + 0:
                        break
            collectors_to_assigned_atms[dict_queue[min(dict_queue.keys())]].append(extra_atm)

        for collector, atms in collectors_to_assigned_atms.items():
            for atm in atms:
                collector.add_atm_to_queue(atm[0])


class Collector:
    def __init__(self, longitude, latitude, number, colour: str):
        self.__number = number
        self.__colour = colour
        self.collector_atms_queue = queue.Queue()
        self.AMT_PROCESS_TIME = random.gauss(12, 3)
        self.__start_point_latitude = latitude
        self.__start_point_longitude = longitude
        self.__current_latitude = self.__start_point_latitude
        self.__current_longitude = self.__start_point_longitude
        self.__work_time_minutes = 480  # work time in minutes a day

    def __str__(self):
        return f'Point {self.__start_point_longitude} {self.__start_point_latitude}'

    def get_colour(self):
        return self.__colour

    def get_number(self):
        return self.__number

    def decrease_left_work_time(self, value) -> bool:
        self.__work_time_minutes = (self.__work_time_minutes - value) if (self.__work_time_minutes - value) > 0 else 0
        if self.__work_time_minutes == 0:
            return False
        return True

    def refresh_work_time(self):
        self.__work_time_minutes = 480

    def get_atm_process_time(self):
        self.AMT_PROCESS_TIME = random.gauss(20, 5)
        return self.AMT_PROCESS_TIME

    def get_queue_size(self):
        return self.collector_atms_queue.qsize()

    def change_current_coordinates(self, *coordinates):
        self.__current_latitude = coordinates[0]
        self.__current_longitude = coordinates[1]

    def work_for(self, time_period):
        self.decrease_left_work_time(time_period)

    def get_coordinates(self) -> list:
        return [self.__start_point_longitude, self.__start_point_latitude]

    def add_atm_to_queue(self, atm_to_add):
        self.collector_atms_queue.put(atm_to_add)

    def process_queued_atms(self):
        self.refresh_work_time()
        counter = 0
        total_distance = 0.0
        atms_array = []
        while not self.collector_atms_queue.empty():
            counter += 1
            current_atm = self.collector_atms_queue.get()
            current_atm.refresh_atm()
            atms_array.append(current_atm.get_coordinates())

        atms_array.insert(0, self.get_coordinates())

        sources = np.array(atms_array)
        distance_matrix = great_circle_distance_matrix(sources)
        permutation, distance = solve_tsp_dynamic_programming(distance_matrix)

        result_atms_array = []

        for number in permutation:
            if len(result_atms_array):
                folium.Marker(atms_array[number], popup=f"<i>ATM №{len(result_atms_array)}</i>",
                              icon=folium.Icon(color=self.__colour, icon='asdf')).add_to(
                    gp.map_plot_route)
            result_atms_array.append(atms_array[number])

        response = gp.add_route_to_map(gp.map_plot_route, self.get_coordinates(), self.get_coordinates(),
                                       self.__colour, result_atms_array)
        if response:
            total_distance = gp.get_overall_distance_in_meters_multiple(response)
            work_time = gp.get_overall_time_in_seconds_multiple(response)
            self.work_for(work_time / 60 + self.get_atm_process_time() * geoapi.get_waypoints_quantity(response))

        db.connection.commit()
        print(
            f"Time left after work: {int(self.__work_time_minutes)} minutes,"
            f"total driven distance is {int(total_distance / 1000)} km"
        )


def init_atms():
    result = db.get_all_rows_from_table('atms_data')
    for row in result:
        atm_to_insert = Atm([row["longitude"], row["latitude"]], row["atm_id"])
        atms.add_atm(atm_to_insert)


def init_collectors() -> list:
    collectors_list = [Collector(MOSCOW_COLLECTORS_START_POINTS[0][0], MOSCOW_COLLECTORS_START_POINTS[0][1], 1,
                                 "red"),
                       Collector(MOSCOW_COLLECTORS_START_POINTS[1][0], MOSCOW_COLLECTORS_START_POINTS[1][1], 2,
                                 "green"),
                       Collector(MOSCOW_COLLECTORS_START_POINTS[2][0], MOSCOW_COLLECTORS_START_POINTS[2][1], 3,
                                 "blue"),
                       Collector(MOSCOW_COLLECTORS_START_POINTS[3][0], MOSCOW_COLLECTORS_START_POINTS[3][1], 4,
                                 "black"),
                       Collector(MOSCOW_COLLECTORS_START_POINTS[4][0], MOSCOW_COLLECTORS_START_POINTS[4][1], 5,
                                 "orange")]
    for collector in collectors_list:
        folium.Marker(
            collector.get_coordinates(),
            opup="<b>Collectors start point</b>",
            icon=folium.Icon(color=collector.get_colour(), icon='home')
        ).add_to(gp.map_plot_route)
    return collectors_list


atms = MoscowAtms()

init_atms()

collectors = MoscowCollectors(init_collectors())
