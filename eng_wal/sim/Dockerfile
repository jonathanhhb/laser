FROM python:3.9

WORKDIR /app

RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/sim_ew_jb_animation.html.gz
RUN gunzip sim_ew_jb_animation.html.gz
RUN mv sim_ew_jb_animation.html /app/index.html 

# Expose port 80
EXPOSE 80

# Run a Python HTTP server to serve the HTML file
CMD ["python", "-m", "http.server", "80"]

