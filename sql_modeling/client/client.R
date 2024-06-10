#' This is a client script for running a LASER model as a service at a specific 
#' endpoint.
#' You send 4 parameters and wait for the summary of major metrics to be returned.
#' This script sends a POST request to a specified URL with a JSON payload containing 
#' parameters for an epidemiological model. The payload includes 'base_infectivity', 
#' 'migration_fraction', 'seasonal_multiplier', and 'duration'. After constructing the 
#' JSON payload, the script performs the POST request and checks the response status. 
#' If the request is successful, it prints the response content; otherwise, it prints 
#' an error message with the status code.

library(httr)
library(jsonlite)

# Define the URL and the payload
url <- "http://172.18.0.2:5000/submit"
payload <- list(
  base_infectivity = 0.5,
  migration_fraction = 0.1,
  seasonal_multiplier = 1.2,
  duration = 2
)

# Convert the payload to JSON
json_payload <- toJSON(payload, auto_unbox = TRUE)

# Perform the POST request
response <- POST(
  url, 
  add_headers("Content-Type" = "application/json"), 
  body = json_payload, 
  encode = "json"
)

# Check the response
if (status_code(response) == 200) {
  print(content(response, "text"))
} else {
  print(paste("Request failed with status:", status_code(response)))
}

