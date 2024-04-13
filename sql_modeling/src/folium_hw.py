import folium
from folium.plugins import HeatMapWithTime
import numpy as np
import random
import pdb

# Generate random data for 10 locations near London
locations = [(51.5074 + random.uniform(-0.1, 0.1), -0.1278 + random.uniform(-0.1, 0.1)) for _ in range(10)]

# Generate random data for 365 days
#data = np.random.rand(365, 10)

# Normalize the data between 0 and 1
#data = (data - np.min(data)) / (np.max(data) - np.min(data))
data = []
pdb.set_trace()
for t in range(365):
    data.append( [ [ location[0], location[1], random.random() ] for location in locations  ] )

# Create map centered around London
m = folium.Map(location=[51.5074, -0.1278], zoom_start=10)

# Create HeatMapWithTime
#hm = HeatMapWithTime(data, index=[str(i) for i in range(365)], auto_play=True, radius=15)
hm = HeatMapWithTime(data, auto_play=True, radius=15)

# Add HeatMapWithTime to map
hm.add_to(m)

# Save the map to an HTML file
m.save("animated_heatmap_toy.html")

