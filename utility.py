import os
import json
from math import radians, cos, sin, sqrt, atan2
import geoapi as gp


HEADER = 64
PORT = 12500
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

counter_for_map = 0


def get_distance_between_geocoord(first_point: list, second_point: list):
    latitude_1 = radians(first_point[0])
    longitude_1 = radians(first_point[1])
    latitude_2 = radians(second_point[0])
    longitude_2 = radians(second_point[1])
    longitude_difference = longitude_1 - longitude_2
    y = sqrt(
        (cos(latitude_2) * sin(longitude_difference)) ** 2
        + (cos(latitude_1) * sin(latitude_2) - sin(latitude_1) * cos(latitude_2) * cos(longitude_difference)) ** 2
    )
    x = sin(latitude_1) * sin(latitude_2) + cos(latitude_1) * cos(latitude_2) * cos(longitude_difference)
    coefficient = atan2(y, x)
    return 6372.8 * coefficient


def convert_atms_to_json(atms_list: list) -> str:
    result = []
    for atm in atms_list:
        result.append(atm.get_coordinates())
    return json.dumps(result)


def send_coordinates(conn_socket, atms_collection):
    json_data = convert_atms_to_json(atms_collection.get_first_n_sorted_atms(50))
    msg_length = len(json_data)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn_socket.sendall(send_length)
    conn_socket.sendall(json_data.encode(FORMAT))


def send_html(conn_socket, atms_collection, collectors, folium_instance):
    simulate_day_with_collectors(1, atms_collection, collectors, folium_instance)
    file = open(f'map_day_{counter_for_map}.html', 'rb')
    msg_length = os.path.getsize(f'map_day_{counter_for_map}.html')
    data = file.read(10485760)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn_socket.sendall(send_length)
    conn_socket.sendall(data)
    file.close()


def send_str(conn_socket, str_to_send):
    error_response = str_to_send
    send_length = str(len(error_response)).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn_socket.sendall(send_length)
    conn_socket.sendall(str(error_response).encode(FORMAT))


def print_data_for_a_new_day(atms_collection):
    for atm in atms_collection.get_first_n_sorted_atms(50):
        print(
            f'in: {atm.get_current_input_volume()} / out: {atm.get_current_output_volume()} '
            f'banknotes at {atm.get_longitude()} {atm.get_latitude()}')
    print("------------------------------")


def add_collectors_start_markers_on_map(map_instance, collectors, folium_instance):
    for collector in collectors:
        folium_instance.Marker(
            collector.get_coordinates(),
            opup="<b>CollectorS start point</b>",
            icon=folium_instance.Icon(color=collector.get_colour(), icon='home')
            ).add_to(map_instance)


def simulate_day_with_collectors(days, atms_collection, collectors, folium_instance):
    global counter_for_map
    for k in range(days):  # simulation for days, collectors must process at least 50 atms a day
        atms_collection.simulate_one_day()
        collectors_list = collectors.get_collectors_list()
        atms_collection.distribute_atms_to_collectors(collectors_list)
        for collector in collectors_list:
            collector.process_queued_atms()
        counter_for_map = counter_for_map + 1 if counter_for_map < 5 else 1
        gp.map_plot_route.save(f"./map_day_{counter_for_map}.html")
        gp.map_plot_route = folium_instance.Map()
        gp.map_plot_route = folium_instance.Map(location=[55.738297, 37.630306], zoom_start=11)
        add_collectors_start_markers_on_map(gp.map_plot_route, collectors.get_collectors_list(), folium_instance)


def full_atms_refresh(atms_collection, db_connection):
    for a in atms_collection.get_atms():
        a.refresh_atm()
    db_connection.commit()
