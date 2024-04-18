0) Install sqlite3 and pip install folium.
1) Run simulation and produce simulation_output.csv. Details omitted.
2) Get cities.csv. Easy to generate from engwaldata or just run:
```
wget https://packages.idmod.org:443/artifactory/idm-data/laser/cities.csv
```
3) Open sqlite shell and load/create ew_sim.db:
```
sqlite3 /path/to/ew_sim.db
```
4) Import simulation output, etc.
```
.mode csv
.drop table engwal
.import simulation_output.csv engwal
.import cities.csv cities
CREATE VIEW cases AS SELECT Timestep, Node, Name, Latitude, Longitude, "New Infections" from engwal, cities where engwal.Node = cities.ID
```
5) exit sqlite3.
6) Run main script to create big HTML file.
```
python3 viz/folium_animate_from_sqlite.py 
```
7) Load simulation_animation.html from browser
