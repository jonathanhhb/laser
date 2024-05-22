FROM python:3.9

WORKDIR /app

COPY service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update
RUN apt install -y wget
RUN apt install -y g++

COPY service/. .
RUN mkdir static
RUN mv spinner.css static/

COPY src/settings.py .
COPY src/demographics_settings_ew.py .
RUN mv demographics_settings_ew.py demographics_settings.py 
COPY src/tlc.py .
COPY src/sir_numpy_c.py .
COPY src/sir_numpy.py .
COPY src/sir_sql.py .
COPY src/report.py .
COPY src/update_ages.cpp .
RUN g++ -shared -fPIC -O3 -march=native -flto -fpermissive -fopenmp update_ages.cpp -o update_ages.so
COPY src/model_numpy/eula.py model_numpy/eula.py
COPY src/model_sql/eula.py model_sql/eula.py
COPY src/post_proc.py .
RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/engwal_modeled.csv.gz
RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/attraction_probabilities.csv.gz
RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/engwal_cities.csv -O cities.csv
RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/engwal_pops.csv -O pops.csv
RUN gunzip attraction_probabilities.csv.gz
COPY src/viz/plot_spatial.py .

COPY service/fits.npy .
COPY src/cbrs.csv .
COPY src/births.csv .

CMD ["python", "app.py"]

