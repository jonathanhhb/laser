# Workflow for Creating Folium Animations (HTML/JS) from Model Output

This document outlines the step-by-step process for converting a simulation output file (`simulation_output.csv`) into a web animation using Folium, a Python library for creating interactive maps.

## Prerequisites

Ensure you have the following prerequisites installed:

- `sqlite3`
- `folium` Python library

You can install `folium` using pip:

```bash
pip install folium
```

## Workflow Steps

1. Run Simulation:

Execute the simulation process to generate the simulation_output.csv file. That file has the following columns/structure:

```
Timestep,Node,Susceptible,Infected,New Infections,Recovered,Births,Deaths
```

We shall only be using the Timestep, Node, and New Infections columns here.

Details of the simulation process are omitted here.

2. Get Cities Data:

Obtain the cities.csv file. This file contains data about cities and can be generated from engwaldata or downloaded directly using the following command:

```
wget https://packages.idmod.org:443/artifactory/idm-data/laser/cities.csv
```

3. Open the sqlite shell and load or create the `ew_sim.db` database:
```
sqlite3 /path/to/ew_sim.db
```

4. Import Data into Database:

In the SQLite shell, import the simulation output and cities data into the database and create a view for easier querying:
```
.drop table if exists engwal
.import simulation_output.csv engwal
.import cities.csv cities
CREATE VIEW cases AS
SELECT Timestep, Node, Name, Latitude, Longitude, "New Infections"
FROM engwal, cities
WHERE engwal.Node = cities.ID;
```
5. Exit Sqlite Shell:

Exit the SQLite shell once the data has been imported and the view has been created.

6. Run Main Script:
```
python3 viz/folium_animate_from_sqlite.py
```

7. View Animation
Open a web browser and load the simulation_animation.html file to view the animation.
