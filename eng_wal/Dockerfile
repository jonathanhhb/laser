FROM tiangolo/uwsgi-nginx:python3.9

# Create a directory for your application code
WORKDIR /app

# Copy your application code into the container
COPY . /app

# Set permissions on the necessary directories
USER root
RUN chmod 777 /etc/nginx/
USER nginx

RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/measles_ew_animation.html 
RUN mkdir -p /var/www/html
RUN mv measles_ew_animation.html /var/www/html/index.html 
