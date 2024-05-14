#!/bin/bash

# Directory paths
sandbox_dir="../../sandbox"
src_dir="../sql_modeling/src" 

# Prompt the user to choose between England & Wales and CCS
PS3="Choose an option: "
options=("England & Wales" "CCS")
select choice in "${options[@]}"
do
    case $REPLY in
        1)
            england_wales="England & Wales"
            break
            ;;
        2)
            ccs="CCS"
            break
            ;;
        *)
            echo "Invalid option. Please choose 1 or 2."
            ;;
    esac
done

# Use the chosen value as needed
if [[ -n $england_wales ]]; then
    echo "You chose England & Wales."
elif [[ -n $ccs ]]; then
    echo "You chose CCS."
fi


# Create the sandbox directory if it doesn't exist
mkdir -p "$sandbox_dir"

pushd $sandbox_dir

# Create symlinks for each file or directory in src_dir
ln -sfn "$src_dir/report.py" 
ln -sfn "$src_dir/sir_sql.py"
ln -sfn "$src_dir/makefile"
ln -sfn "$src_dir/utils"
ln -sfn "$src_dir/sir_numpy.py"
ln -sfn "$src_dir/model_numpy"
ln -sfn "$src_dir/model_sql"
ln -sfn "$src_dir/sir_numpy_c.py"
ln -sfn "$src_dir/update_ages.cpp"
ln -sfn "$src_dir/tlc.py"
ln -sfn "$src_dir/makefile"

cp "$src_dir/../service/fits.npy" .
cp "$src_dir/settings.py" .

if [[ -n $england_wales ]]; then
    wget https://packages.idmod.org:443/artifactory/idm-data/laser/engwal_modeled.csv.gz
    wget https://packages.idmod.org:443/artifactory/idm-data/laser/attraction_probabilities.csv.gz
    gunzip attraction_probabilities.csv.gz
    cp "$src_dir/demographics_settings_ew.py" ./demographics_settings.py
elif [[ -n $ccs ]]; then
    cp "$src_dir/demographics_settings_1node.py" ./demographics_settings.py
    make
fi
make update_ages.so

echo "Symlinks & files created in $sandbox_dir"

