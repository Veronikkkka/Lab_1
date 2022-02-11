"""Lab 1 Task 2(map)"""
from haversine import haversine
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
import numpy as np
import folium
import argparse

def get_info_from_user():
    """
    str -> list
    Get arguments from command line
    Return list with all of them
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type = str)
    parser.add_argument('lattitude', type = float)
    parser.add_argument('longtitude', type = float)
    parser.add_argument('path', type = str)
    args = parser.parse_args()
    year = args.year
    lantitude = args.lantitude
    longtitude = args.longtitude
    path = args.path
    return year, lantitude, longtitude, path

def read_file_and_create_loc_list(year, lattitude, longtitude, path):
    """
    str -> list
    Get all arguments and return list that consists
    all info: name, distance from start point, lat- and long-titude
    >>> read_file_and_create_loc_list("1890", 50.4500336, 30.5241361, "locations.list")[:1]
    [("London's Trafalgar Square", 2133.415074713724, 51.508037, -0.12804941070724718)]
    """
    geolocator = Nominatim(user_agent="my_user_agent")
    start_cords = [lattitude, longtitude]
    file = open(path).readlines()
    name_year_location = []
    locations_films = []

    for line in file[14:]:
        if line.__contains__("("+year+")"):
            line = line.replace("\n", "")
            if line != "":
                line_ = line.split("\t")
                line_[0] = line_[0].split(" {")[0]
                name, year = line_[0][:-7], line_[0][-5:-1]
                # print(line_[0], line_[0][-5:-1])
                if line_[-1].find("(") == -1:
                    name_year_location.append((name, year, line_[-1]))
                    try:
                        loc = geolocator.geocode(line_[-1])
                    except GeocoderUnavailable:
                        index_ = line_[-1].find(',')
                        loc = line_[-1][index_+1:]
                        # print("HERE1")
                    while loc is None:
                        index_ = line_[-1].find(',')
                        new_line = line_[-1][index_+1:]
                        # print(new_line, "line_[-1]", line_[-1], index_, line)
                        line_[-1] = new_line
                        loc = geolocator.geocode(new_line)
                        # print("LOC", loc)
                else:
                    name_year_location.append((name, year, line_[-2]))
                    try:
                        loc = geolocator.geocode(line_[-2])
                    except GeocoderUnavailable:
                        index_ = line_[-2].find(',')
                        loc = line_[-2][index_+1:]
                        # print("HERE2")
                    while loc is None:
                        index_ = line_[-2].find(',')
                        new_line = line_[-2][index_+1:]
                        # print(new_line, "line_[-2]", line_[-2], index_, line)
                        line_[-2] = new_line
                        # print(line_)
                        loc = geolocator.geocode(new_line)
                        # print("LOC", loc)
                try:
                    dist = haversine((start_cords[0], start_cords[1]), (loc.latitude, loc.longitude))
                    if (name, dist, loc.latitude, loc.longitude) not in locations_films:
                        locations_films.append((name, dist, loc.latitude, loc.longitude))
                except:
                    # print(line_, "ERROR")
                    pass
    return locations_films
# print(locations_films, len(locations_films))
# print(read_file_and_create_loc_list("1880", 50.4500336, 30.5241361, "locations.list"))
def get_result_list(locations_films: list):
    """
    list -> list
    Get results from previous function
    and find ten the closest locations
    to start point. If locations are equal
    change them. Return the list with full info
    about these 10 locations
    >>> get_result_list(read_file_and_create_loc_list("1895", 50.4500336, 30.5241361, "locations.list"))[2:3]
    [('Place des Cordeliers à Lyon', 1966.1442908584631, 45.7635002, 4.8370379)]
    """
    if len(locations_films) > 10:
        cords = np.array([elem[1] for elem in locations_films])
        # print(cords)
        indexes = np.argpartition(cords, 10)[:10]
        # print(indexes)
        result = []
        for elem in indexes:
            result.append(locations_films[elem])
            # print(locations_films[elem][1])
        # print(name_year_location)
    else:
        result = locations_films
    # print("RES",result)
    unavailable_cords = []
    result_after_relocate = []
    dif = 0.0000599
    for i in result:
        if (i[2], i[3]) in unavailable_cords:
            len_1 = len(unavailable_cords)
            new_1, new_2 = i[2], i[3]
            while (new_1, new_2) in unavailable_cords:
                new_1 += dif + 0.00001
                new_2 += dif
                # print(new_1, new_2)
            dif = dif*(-1)+0.000008
            unavailable_cords.append((new_1, new_2))
            result_after_relocate.append((i[0], i[1], new_1, new_2))
        else:
            unavailable_cords.append((i[2], i[3]))
            result_after_relocate.append(i)
    return result_after_relocate

def create_map(result_after_relocate:list, year:str, lattitude: float, longtitude:float):
    """
    list -> None
    Get list with info about 10 closest locations
    create map with three layers(map, points)
    """
    map = folium.Map(location=[50.4500336, 30.5241361],zoom_start=4)
    fg = folium.FeatureGroup(name="Films native locations")
    fg1 = folium.FeatureGroup(name="Start location")
    html = """<h4 style="color: #a30fdf">{}:</h4>
    Year: {}, <br>
    Distance: {}
    <div>
    """
    # k = 0
    for i in result_after_relocate:
        iframe = folium.IFrame(html=html.format(i[0], year, str(i[1])+" km"), width=270, height=100)
        fg.add_child(folium.Marker(location=[i[2], i[3]],popup=folium.Popup(iframe), 
                                   icon=folium.Icon(color="purple")))
        # k += 1
    fg1.add_child(folium.CircleMarker(location=[lattitude, longtitude], fill_color = "green", color= "green", radius=20))
    # print(k)
    # fg.add_child(folium.Marker(location=[49.817599, 24.023978],popup=folium.Popup(iframe), icon=folium.Icon(color="green")))
    map.add_child(fg, name="fg")
    map.add_child(fg1, name="fg1")
    map.add_child(folium.LayerControl())
    map.save('Map_8.html')
# print("latitude is :" ,loc.latitude,"\nlongtitude is:" ,loc.longitude)
def main():
    """
    This function call all functions in right order
    """
    year, lattitude, longtitude, path = get_info_from_user()
    # year = "1896"
    # lattitude, longtitude = 50.4500336, 30.5241361
    # path = "locations.list"
    res = read_file_and_create_loc_list(year, lattitude, longtitude, path)
    result = get_result_list(res)
    create_map(result, year, lattitude, longtitude)

if __name__ == "main":
    main()
# import doctest
# doctest.testmod()
