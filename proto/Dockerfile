FROM python:3.9-slim

WORKDIR /app

COPY service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update
RUN apt install -y wget

COPY service/. .
RUN mkdir static
RUN mv spinner.css static/

COPY service/app.py .
COPY consolidate.py .
COPY dynamic_property.py .
COPY engwal.py .
COPY engwaldata.py .
COPY gcpopulation.py .
COPY groupedcommunity.py .
COPY engwaldist.npy .


CMD ["python", "app.py"]

