FROM tiangolo/uwsgi-nginx:python3.9

#RUN apt-get update && apt-get install -y wget

RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/measles_ew_animation.html 
RUN mkdir -p /var/www/html
RUN mv measles_ew_animation.html /var/www/html/index.html 
