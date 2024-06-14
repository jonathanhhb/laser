- go to sql_modeling/src

- make setup

- Pick 2 (CCS)

- pushd ../../sandbox

- make run (to confirm everything runs as expected)

- sudo docker-compose up

- make note of url 

- pushd ../sql_modeling/client

- edit calibrate.py and set url to the <url>/submit

- edit calibrate.py to set migration_factor to 0.

- python3 calibrate.py
