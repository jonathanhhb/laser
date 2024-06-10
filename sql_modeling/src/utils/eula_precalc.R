# This script simulates population changes over time based on mortality rates to create necessary
# input files for a LASER prototype model.
#
# Purpose:
# This script reads demographic data from a file and simulates the population dynamics
# over a period of 20 years by calculating expected deaths based on age-specific mortality rates.
# The output is written to a specified CSV file.
#
# Dependencies:
# - data.table: For fast data reading and manipulation.
# - jsonlite: For handling JSON data (if needed in the future).
# - httr: For making HTTP requests (if needed in the future).
#
# Usage:
# Rscript eula_preproc.R eula_20yr_agebins.csv
#
# Required variables in demographics_settings.R:
# - eula_file: Filename for the EULA binned file.
#
# Assumptions:
# Assuming demographics_settings.R contains the required variables and is in the same directory,
# as well as the eula_file csv created by 'create_pop_as_csv.R'.

library(data.table) # Ensure data.table is loaded

# Function to check for required variables in demographics_settings.R
check_required_variables <- function( env ) {
  required_vars <- c("eula_file")

  missing_vars <- sapply(required_vars, function(var) {
    !exists(var, envir = env)
  })

  if (any(missing_vars)) {
    missing_var_names <- required_vars[missing_vars]
    stop(paste("Missing required variables in demographics_settings.R:", paste(missing_var_names, collapse = ", ")))
  }
}

settings <- new.env()
source("demographics_settings.R", local = settings)
check_required_variables(settings)

# Initialize the eula structure
init <- function() {
  eula <- list()
  data <- fread(settings$eula_file, skip = 1)
  
  for (i in 1:nrow(data)) {
    row <- data[i, ]
    node <- as.character(as.integer(row[[1]]))  # Convert node to character
    age <- as.integer(as.numeric(row[[2]]))
    total <- as.integer(row[[3]])
    
    if (!(node %in% names(eula))) {
      eula[[node]] <- list()
    }
    
    eula[[node]][[as.character(age)]] <- total  # Convert age to character
  }
  return(eula)
}

# Probability of dying array
makeham_parameter <- 0.008
gompertz_parameter <- 0.04
age_bins <- 0:101
probability_of_dying <- 2.74e-6 * (makeham_parameter + exp(gompertz_parameter * (age_bins - age_bins[1])))

#print("Probability of dying for each age:")
#print(probability_of_dying)

# Header and data writing functions
writeHeader <- function(file) {
  writeLines("t,node,pop", con = file)
}

writeData <- function(file, t, node, pop) {
  writeLines(paste(t, node, pop, sep = ","), con = file)
}

# Output file setup
args <- commandArgs(trailingOnly = TRUE)
output_file <- args[1]  # Make sure args[1] contains the output file path
output_file_conn <- file(output_file, "w")
on.exit(close(output_file_conn))

writeHeader(output_file_conn)

# Initialize eula
eula <- init()
#print("Initialized eula:")
#print(eula)

# Check structure of eula before the main loop
for (node in names(eula)) {
  #cat("Node:", node, "\n")
  #print(names(eula[[node]]))
}

# Calculate the expected deaths and new population for the next 20 years
for (t in 1:(20 * 365)) {
  for (node in names(eula)) {
    expected_deaths <- rep(0, length(eula[[node]]))
    #cat("Processing node:", node, "at time:", t, "\n")
    #print(names(eula[[node]])) # Print names of ages to verify structure
    
    for (age in names(eula[[node]])) {
      age_index <- as.integer(age)
      count <- eula[[node]][[age]]
      if (count > 0) {
        expected_deaths[age_index + 1] <- rbinom(1, count, probability_of_dying[age_index + 1])
      }
    }
    #cat("Expected deaths for node", node, "at time", t, ":", expected_deaths, "\n")
    
    for (age in names(eula[[node]])) {
      age_index <- as.integer(age)
      eula[[node]][[age]] <- eula[[node]][[age]] - expected_deaths[age_index + 1]
    }
    
    node_time_pop <- sum(unlist(eula[[node]]))
    #cat("Population for node", node, "at time", t, ":", node_time_pop, "\n")
    writeData(output_file_conn, t, node, node_time_pop)
  }
}

