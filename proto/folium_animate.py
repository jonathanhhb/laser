import folium
import pdb

from folium.plugins import HeatMapWithTime
from engwaldata import data as engwal

# Create a map centered at a specific location
m = folium.Map(location=(engwal.places['London'].latitude,engwal.places['London'].longitude), zoom_start=12)

# Create a list to store the data for HeatMapWithTime
data = []

max_cases = 4103 # 0
all_cities = list(engwal.places.keys())
# Iterate over each place in engwal.places
for t in range(len(engwal.places["London"].cases)):
    data.append([[engwal.places[place].latitude, engwal.places[place].longitude, engwal.places[place].cases[t]] for place in all_cities])
    #pdb.set_trace()
    #max_cases = max(item[2] for item in data[-1])  # Find the maximum case value
    data[-1] = [ [ item[0], item[1], item[2]/max_cases ] for item in data[-1] ]

color_map = {
        0: 'blue',
        0.5: 'green', 
        1: 'red'
    }
# Create HeatMapWithTime layer
heat_map = HeatMapWithTime(data,use_local_extrema=True)

# Add HeatMapWithTime layer to the map
heat_map.add_to(m)

# Save the map as an HTML file
m.save('disease_map_animation.html')

