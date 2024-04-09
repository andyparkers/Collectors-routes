import json
import requests
import folium

url = "https://route-and-directions.p.rapidapi.com/v1/routing"

headers = {
        "X-RapidAPI-Key": "*****************************************",
        "X-RapidAPI-Host": "route-and-directions.p.rapidapi.com"
    }

map_plot_route = folium.Map(location=[55.738297, 37.630306], zoom_start=11)             # start point of .html file initial view approximately in the middle of Moscow


def get_index_data(str_response, index_number) -> list:
    return [
        json.loads(str_response.text)['features'][0]['geometry']['coordinates'][0][index_number][1],
        json.loads(str_response.text)['features'][0]['geometry']['coordinates'][0][index_number][0]
    ]


def get_steps_array(str_response) -> list:
    result = []
    for point in range(len(list(json.loads(str_response.text)['features'][0]['properties']['legs'][0]['steps'])) - 1):
        pair = [
            json.loads(str_response.text)['features'][0]['properties']['legs'][0]['steps'][point]['from_index'],
            json.loads(str_response.text)['features'][0]['properties']['legs'][0]['steps'][point]['to_index']
        ]
        result.append(pair)
    return result


def get_coordinates(str_response):
    result = []
    for pair in get_steps_array(str_response):
        result.append([get_index_data(str_response, pair[0]), get_index_data(str_response, pair[1])])
    return result


def get_all_coordinates_multiple(str_response) -> list:
    result = []
    try:
        if str_response.text == "{\"statusCode\":400,\"error\":\"Bad Request\",\"message\":\"No path could be found for input\"}":
            return []
        for i in range(len(list(json.loads(str_response.text)['features'][0]['geometry']['coordinates'])) - 1):
            for j in range(len(list(json.loads(str_response.text)['features'][0]['geometry']['coordinates'][i])) - 1):
                pair = [
                    json.loads(str_response.text)['features'][0]['geometry']['coordinates'][i][j][1],
                    json.loads(str_response.text)['features'][0]['geometry']['coordinates'][i][j][0]
                ]
                result.append(pair)
        return result
    except KeyError:
        print(f"Bad response {str_response.text}")


def get_overall_distance_in_meters(str_response) -> int:
    return json.loads(str_response.text)['features'][0]['properties']['legs'][0]['distance']


def get_overall_distance_in_meters_multiple(str_response) -> int:
    return json.loads(str_response.text)['features'][0]['properties']['distance']


def get_overall_time_in_seconds_multiple(str_response) -> int:
    return json.loads(str_response.text)['features'][0]['properties']['time']


def get_overall_time_in_seconds(str_response) -> int:
    return json.loads(str_response.text)['features'][0]['properties']['legs'][0]['time']


def get_response_from_api(query_str: dict):
    return requests.request("GET", url, headers=headers, params=query_str)


def get_distance_with_api(coord_1, coord_2, *args) -> int:
    querystring_nested = f"{{\"waypoints\": \"{coord_1[0]},{coord_1[1]}|{coord_2[0]},{coord_2[1]}\", \"mode\": \"drive\"}}"
    response = requests.request("GET", url, headers=headers, params=json.loads(querystring_nested))
    print(get_steps_array(response))
    return get_overall_distance_in_meters(response)


def get_waypoints_quantity(str_response) -> int:
    return len(json.loads(str_response.text)['features'][0]['properties']['waypoints'])


def save_html_route_map(folium_map_instance, start_point: list, end_point: list, html_name, colour="blue", *intermediate_points):           # add simular function with '*args' as multiple coordinates
    coordinates = f"{start_point[0]},{start_point[1]}"
    for coordinates in intermediate_points:
        coordinates += f"|{coordinates[0]},{coordinates[1]}"
    coordinates += f"|{end_point[0]},{end_point[1]}"
    query_string = {"waypoints": coordinates, "mode": "drive"}

    response = requests.request("GET", url, headers=headers, params=query_string)

    route_points = get_all_coordinates_multiple(response)

    folium.PolyLine(route_points, colour=colour).add_to(folium_map_instance)
    folium_map_instance.save(f"./{html_name}.html")


def add_route_to_map(folium_map_instance, start_point: list, end_point: list, colour="blue", *intermediate_points):
    coordinates_query = f"{start_point[0]},{start_point[1]}"
    for coordinates in intermediate_points[0]:
        coordinates_query += f"|{coordinates[0]},{coordinates[1]}"
    coordinates_query += f"|{end_point[0]},{end_point[1]}"
    query_string = {"waypoints": coordinates_query, "mode": "drive"}

    response = requests.request("GET", url, headers=headers, params=query_string)

    route_points = get_all_coordinates_multiple(response)
    if not route_points:
        return False
    folium.PolyLine(route_points, colour=colour).add_to(folium_map_instance)

    return response
