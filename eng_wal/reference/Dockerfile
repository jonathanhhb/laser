FROM python:3.9

WORKDIR /app

RUN wget https://packages.idmod.org:443/artifactory/idm-data/laser/measles_ew_animation.html 
RUN mv measles_ew_animation.html /app/index.html 

# Expose port 80
EXPOSE 80

# Run a Python HTTP server to serve the HTML file
CMD ["python", "-m", "http.server", "80"]

