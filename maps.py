import ssl
import folium
from geopy.geocoders import ArcGIS


# Disable SSL certificate verification (for MacOS)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


def read_file(file_name):
    '''
    (str) -> (list)
    This function reads data from file and returns it in list
    '''
    lst = []
    with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.readlines():
            line = line.strip('\n')
            lst.append(line.split('\t'))
    return lst


def find_films(lst, year):
    '''
    (list, int) -> (list)
    This function finds films of an exact year and returns list with their
    locations
    '''
    locations_lst = []
    for i in lst:
        for j in i:
            j = j.split()
            if ("(" + str(year) + ")") in j:
                locations_lst.append(i[-1])
            else:
                continue
    return locations_lst


def geolocation(place):
    '''
    (list) -> (float, float)
    This function returns altitude and longitude of an exact place
    >>>geolocation('Lviv, Ukraine')
    (49.84441000000004, 24.02543000000003)
    '''
    location = ArcGIS(timeout=100).geocode(place)
    return location.latitude, location.longitude


def build_map(year):
    '''
    (str) -> ()
    This function builds map with different layers and creates an HTML file
    '''
    my_map = folium.Map(location=[51.509865, -0.118092], zoom_start=2)

    lst = []

    for i in find_films(read_file("locations.list.txt"), year):
        lst.append(geolocation(i))

    # Adding FILMS feature group
    films = folium.FeatureGroup(name="Films")
    for i in lst:
        films.add_child(folium.Marker(location=i,
                                      icon=folium.Icon(color='black')))

    # Adding POPULATION feature group
    population = folium.FeatureGroup(name="Population")
    population.add_child(folium.GeoJson(data=open('world.json.txt', 'r',
                                        encoding='utf-8-sig').read(),
                                        style_function=lambda x: {
                                            'fillColor': '#88ff4d'
                                            if x['properties']
                                            ['POP2005'] < 10000000
                                            else '#ffcc00'
                                            if 10000000 < x['properties']
                                            ['POP2005'] < 20000000
                                            else '#b30000'}))

    # Adding layers to map
    my_map.add_child(population)
    my_map.add_child(films)
    my_map.add_child(folium.LayerControl())

    # Saving map in HTML file
    my_map.save("Map.html")


user_year = int(input("Enter year you want to see: "))
build_map(user_year)
