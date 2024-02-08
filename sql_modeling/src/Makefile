all: tlc.py

full_pop_seeded.csv: settings.py
	python3 create_pop_as_csv.py

update_ages.so: update_ages.c
	gcc -O3 -march=native -flto -o update_ages.so -shared -fPIC update_ages.c

tlc.py: modeled_pop.csv update_ages.so eula.db
	python3 tlc.py

# 5 is hardcoded. Should really read from settings.
modeled_pop.csv: full_pop_seeded.csv
	./eula_preproc.sh full_pop_seeded.csv 5

eula.db: modeled_pop.csv
	python3 csv_to_db.py eula_pop.csv

run: # eula.db modeled_pop.csv
	python3 tlc.py

clean:
	rm -f pop_input.csv

test:
	python3 tests/test_calc_new_inf.py
