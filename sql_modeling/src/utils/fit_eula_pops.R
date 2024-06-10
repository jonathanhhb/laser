# This script performs a linear fit on population data grouped by nodes and saves the fit parameters.
#
# Purpose:
# This script reads population data from a CSV file, performs a linear regression on the data grouped by node,
# and saves the fit parameters to an npy file. It is used for creating the mortality related input file used by
# a prototype LASER model.
#
# Dependencies:
# - data.table: For fast data reading and manipulation.
# - reticulate: For interfacing with Python and saving the data in .npy format.
#
# Usage:
# Rscript fit_eula_pops eula_pops_20yr_noaging.csv
#
# Required variables in demographics_settings.R:
# - eula_pop_fits: Filename for saving the fit parameters.
#
# Assumptions:
# - demographics_settings.R contains the required variable and is in the same directory,
# - 20_year_pops.csv file exists as created by eula_preproc.R

library(data.table)
library(reticulate)

# Function to check for required variables in demographics_settings.R
check_required_variables <- function( env ) {
  required_vars <- c("eula_pop_fits")

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

# Function to perform linear fit
linear_fit <- function(x, m, b) {
  return(m * x + b)
}

# Read the CSV file
args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
output_file <- settings$eula_pop_fits

df <- fread(input_file)

# Group data by 'node' and fit a line for each group
fits <- list()
nodes <- unique(df$node)

for (node in nodes) {
  group <- df[node == df$node, ]
  x_data <- group$t
  y_data <- group$pop
  
  # Perform linear regression
  model <- nls(y_data ~ linear_fit(x_data, m, b), start = list(m = 1, b = 0))
  params <- coef(model)
  
  # Save the fit parameters to a list
  fits[[as.character(node)]] <- params
}

# Use reticulate to convert R list to Python dictionary and save as .npy
np <- import("numpy")
fits_dict <- r_to_py(fits)
np$save(output_file, fits_dict)

cat("Fits saved to", output_file, "\n")

