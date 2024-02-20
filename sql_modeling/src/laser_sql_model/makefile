# Define variables
PYTHON := python3
CC := gcc
CFLAGS := -shared -fPIC
DB_SCRIPT := csv_to_db.py
PREPROC_SCRIPT := ./eula_preproc.sh
CREATE_POP_SCRIPT := create_pop_as_csv.py
POP_SEEDED_CSV := pop_seeded.csv
EULA_DB := eula.db
UPDATE_AGES_SO := update_ages.so
MODELED_POP_CSV := modeled_pop.csv
EULA_POP_CSV := eula_pop.csv

# Default target
all: $(EULA_DB) $(MODELED_POP_CSV)

# Rule to build update_ages.so from update_ages.c
$(UPDATE_AGES_SO): update_ages.c
	$(CC) $(CFLAGS) -o $@ $<

# Rule to create eula.db from eula_pop.csv
$(EULA_DB): eula_pop.csv
	rm -f $(EULA_DB)
	$(PYTHON) $(DB_SCRIPT) $<

$(POP_SEEDED_CSV): settings.py
	$(PYTHON) $(CREATE_POP_SCRIPT)

# Rule to create modeled_pop.csv and pop_seeded.csv
$(MODELED_POP_CSV) $(EULA_POP_CSV): $(POP_SEEDED_CSV)
	$(PREPROC_SCRIPT) $(POP_SEEDED_CSV) 5

run:
	python3 tlc.py

# Clean target to remove generated files
clean:
	rm -f $(UPDATE_AGES_SO) $(EULA_DB) $(POP_SEEDED_CSV) $(MODELED_POP_CSV)

# Phony targets
.PHONY: all clean

