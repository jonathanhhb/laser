import folium
import pdb
import pandas as pd
import csv
import sqlite3
import random
import numpy as np
import sys
sys.path.append( "." )

from folium.plugins import HeatMapWithTime
#from engwaldata import data as engwal

# Create a map centered at a specific location
#m = folium.Map(location=(engwal.places['Birmingham'].latitude,engwal.places['Birmingham'].longitude), zoom_start=8) # Create a list to store the data for HeatMapWithTime
birmingham_location = (52.485,-1.86)
m = folium.Map(location=(birmingham_location[0],birmingham_location[1]), zoom_start=8) # Create a list to store the data for HeatMapWithTime

conn = sqlite3.connect('experiments/ew_sim.db')
cursor = conn.cursor()
start_time=800
cursor.execute('SELECT CAST(Timestep AS INT), Latitude, Longitude, CAST("New Infections" AS INT) FROM cases WHERE (CAST(Timestep AS INT)>800)')
raw_data = cursor.fetchall()

# Group the data by timestep
max_infections = 500

grouped_data = {}
for row in raw_data:
    timestep, lat, lon, new_infections = row
    max_infections = max(max_infections, new_infections)  # Update max_infections
    if timestep not in grouped_data:
        grouped_data[timestep] = []
    grouped_data[timestep].append([lat, lon, new_infections]) # 
    #grouped_data[timestep].append([lat, lon, 0.0]) # 

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

max_cases = 500
for t in range(len(grouped_data)-1):
    this_row = []
    for i, location in enumerate( locations ):
        try:
            def renorm( value ):
                if value > max_cases:
                    value = max_cases
                offset = 1 # e-6
                log_value = np.log(value + offset)
                log_min = np.log(0 + offset)
                log_max = np.log(max_cases + offset)
                return (log_value - log_min) / (log_max - log_min)
            case_value = grouped_data[t][i][2]
            case_value = renorm( case_value )
            #print( f"t={t},lat={location[0]},long={location[1]},value={case_value}" )
            #this_row.append( [ location[0], location[1], 0.0 ] )
            #this_row.append( [ location[0], location[1], case_value ] )
            #this_row.append( [ location[0], location[1], random.random()/200 ] )
            this_row.append( [ location[0], location[1], case_value+random.random()/2000 ] )
        except Exception as ex:
            print( f"Exception with t={t}, i={i}." )
            raise ValueError( str( ex ) )
    data.append( this_row )
    #data.append( [ [ location[0], location[1], grouped_data[t][i][2]/max_infections ] for i, location in enumerate(locations) ] )
    #data.append( [ [ location[0], location[1], random.random() ] for location in locations  ] )

#HeatMapWithTime(heatmap_data, radius=15, gradient={0.1: 'blue', 0.3: 'lime', 0.5: 'orange', 1: 'red'}, min_opacity=0.5, max_opacity=0.8, use_local_extrema=True).add_to(m)
#heat_map = HeatMapWithTime(list(grouped_data.values()), radius=15, gradient={0.1: 'blue', 0.3: 'lime', 0.5: 'orange', 1: 'red'}, min_opacity=0.5, max_opacity=0.8, use_local_extrema=True, auto_play=False )

heat_map = HeatMapWithTime(
        data,
        radius=15, 
        gradient={0.0: 'blue', 0.2: 'green', 0.4: 'yellow', 0.6: 'orange', 0.8: 'red'},
        min_opacity = 0.0,
        max_opacity = 0.8,
        #use_local_extrema=True,
        auto_play=True 
    )
heat_map.add_to(m)


# Save the map as an HTML file
m.save('sim_animation.html')

