import folium
import pdb
import pandas as pd
import csv
import sqlite3
import random

from folium.plugins import HeatMapWithTime
from engwaldata import data as engwal

# Create a map centered at a specific location
m = folium.Map(location=(engwal.places['London'].latitude,engwal.places['London'].longitude), zoom_start=7)

# Create a list to store the data for HeatMapWithTime

conn = sqlite3.connect('ew_sim.db')
cursor = conn.cursor()
cursor.execute('SELECT CAST(Timestep AS INT), Latitude, Longitude, CAST("New Infections" AS INT) FROM cases')
raw_data = cursor.fetchall()

# Group the data by timestep
max_infections = 0

grouped_data = {}
for row in raw_data:
    timestep, lat, lon, new_infections = row
    max_infections = max(max_infections, new_infections)  # Update max_infections
    if timestep not in grouped_data:
        grouped_data[timestep] = []
    #grouped_data[timestep].append([lat, lon, new_infections]) # 
    grouped_data[timestep].append([lat, lon, 0.0]) # 

    # Normalize the "New Infections" values
    def normalize():
        for t in grouped_data:
            for p in grouped_data[t]:
                p[2] /= max_infections
    #normalize()

data = []
grouped_data = list(grouped_data.values())
locations=[[ float(elem[0]), float(elem[1]) ] for elem in grouped_data[0]]
#for t in range(365):

for t in range(len(grouped_data)):
    data.append( [ [ location[0], location[1], random.random() ] for location in locations  ] )

#HeatMapWithTime(heatmap_data, radius=15, gradient={0.1: 'blue', 0.3: 'lime', 0.5: 'orange', 1: 'red'}, min_opacity=0.5, max_opacity=0.8, use_local_extrema=True).add_to(m)
#heat_map = HeatMapWithTime(list(grouped_data.values()), radius=15, gradient={0.1: 'blue', 0.3: 'lime', 0.5: 'orange', 1: 'red'}, min_opacity=0.5, max_opacity=0.8, use_local_extrema=True, auto_play=False )

heat_map = HeatMapWithTime(
        #
        data,
        radius=15, 
        #gradient={0.0: 'blue', 0.2: 'green', 0.4: 'yellow', 0.6: 'orange', 0.8: 'red'},
        #min_opacity = 0.0,
        #max_opacity = 0.8,
        #use_local_extrema=False,
        #gradient={0: 'blue', 1: 'red'}, min_opacity=0.0, max_opacity=0.8, use_local_extrema=True,
        auto_play=True 
        )
heat_map.add_to(m)


# Save the map as an HTML file
m.save('sim_animation.html')

