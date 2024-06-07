from flask import Flask, request, render_template_string, send_file, jsonify
import subprocess

app = Flask(__name__)

params_v0 = [
{
	'name': "pop",
	'default': "int(1e7)+1",
        'description': "Total human population (not agents)"
},
{
        'name': 'num_nodes',
	'default': "60",
        'description': "Number of nodes/populations"
},
{
        'name': 'eula_age',
	'default': "5",
        'description': "Age at which we assume initial population is Epidemiologically Uninteresting (Immune)"
},
{
        'name': 'duration',
	'default': "1",
        'description': "Simulation duration in years."
},
{
        'name': 'base_infectivity',
	'default': "1.5e7",
        'description': "Proxy for R0"
},
{
        'name': 'cbr',
	'default': "15",
        'description': "Crude Birth Rate (same for all nodes)"
},
{
        'name': 'campaign_day',
	'default': "60",
        'description': "Day at which one-time demo campaign occurs"
},
{
        'name': 'campaign_coverage',
	'default': "0.75",
        'description': "Coverage to use for demo campaign"
},
{
        'name': 'campaign_node',
	'default': "15",
        'description': "Node to target with demo campaign"
},
{
        'name': 'migration_interval',
	'default': "7",
        'description': "Timesteps to wait being doing demo migration"
},
{
        'name': 'mortality_interval',
	'default': "7",
        'description': "Timesteps between applying non-disease mortality."
},
{
        'name': 'fertility_interval',
	'default': "7",
        'description': "Timesteps between adding new babies."
},
{
        'name': 'ria_interval',
	'default': "7",
        'description': "Timesteps between applying routine immunization of 9-month-olds."
},
]

params = [
        {
            "name": "base_infectivity",
            "type": "float",
            "required": True,
            "min": 0.5,
            "max": 10.0,
            "default": 2.2,
            "description": "The base infectivity rate of the virus. How much contagion is shed each day by each infectious person."
        },
        {
            "name": "migration_fraction",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 1.0,
            "default": 0.05,
            "description": "The fraction of the infectious population that migrates (permanently) each timestep."
        },
        {
            "name": "seasonal_multiplier",
            "type": "float",
            "required": True,
            "min": 0.0,
            "max": 3.0,
            "default": 0.7,
            "description": "The multiplier to account for seasonal effects. There is a base seasonality curve to reflect the school year. Setting this to 0 eliminates seasonality. Making this too high increases the likelihood of elimination during the summer hols."
        },
        {
            "name": "duration",
            "type": "integer",
            "required": True,
            "min": 0,
            "max": 20,
            "default": 4,
            "description": "Duration of the simulation in years."
        }
    ]

def validate_params(data, schema):
    for param in schema:
        name = param['name']
        value = data.get(name)
        if value is None:
            raise ValueError(f"Parameter '{name}' is required.")
        if param['type'] == 'float':
            value = float(value)
        elif param['type'] == 'integer':
            value = int(value)
        else:
            raise TypeError(f"Unsupported type for parameter '{name}': {param['type']}")

        if not (param['min'] <= value <= param['max']):
            raise ValueError(f"Parameter '{name}' must be between {param['min']} and {param['max']} (got {value}).")


# Define the API documentation
API_DOC = """
<h1>Web Service API</h1>
<p>This web service allows you to submit parameters and run the application.</p>
<p>To submit parameters, make a POST request to /submit with the following parameters:</p>
<ul>
  <li>param1: description of parameter 1</li>
  <li>param2: description of parameter 2</li>
  <!-- Add more parameters as needed -->
</ul>
"""

# Define the HTML template for the form
FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Web Service Form</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='spinner.css') }}">
</head>
<body>
  <div id="overlay"></div>
  <div id="spinnerContainer">
    <div class="loading-spinner"></div>
  </div>
  <h1>Submit Parameters</h1>
  <form id="myForm" method="POST" action="/submit">
    <!-- Dynamically generate form fields -->
    <div id="formFields"></div>
    <button type="submit">Submit</button>
  </form>

  <!-- Div to display the returned image -->
  <div id="imageContainer"></div>

  <!-- JavaScript to handle form submission and image display -->
  <script>
    var params = {{ params|tojson }};

    // Define the params list of dictionaries 
    // Function to create text entry fields based on params list
    function createFormFields() {
      var formFieldsHtml = '';
      params.forEach(function(param) {
        formFieldsHtml += '<label for="' + param.name + '">' + param.name + ':</label>';
        formFieldsHtml += '<input type="text" name="' + param.name + '" id="' + param.name + '" value="' + param.default + '"><br>';
        formFieldsHtml += '<small>' + param.description + '</small><br><br>';
      });
      document.getElementById('formFields').innerHTML = formFieldsHtml;
    }

    // Call createFormFields function when the page loads
    window.onload = createFormFields;

    // Function to handle form submission
    document.getElementById('myForm').addEventListener('submit', function(event) {
      event.preventDefault(); // Prevent default form submission

      // Serialize form data
      var formData = new FormData(this);

      // Send form data using AJAX
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/submit', true);

      // Display loading overlay and spinner before sending the request
      var overlay = document.getElementById('overlay');
      var spinner = document.getElementById('spinnerContainer');
      overlay.style.display = 'block';
      spinner.style.display = 'block';

      xhr.onload = function() {
        if (xhr.status === 200) {
          // Remove spinner
          overlay.style.display = 'none';
          spinner.style.display = 'none';
          
          // If request is successful, display the returned image
          var timestamp = new Date().getTime(); // Generate a timestamp
          var imageUrl = 'prevs.png?' + timestamp; // Append timestamp to image URL
          document.getElementById('imageContainer').innerHTML = '<img src="' + imageUrl + '" alt="prevs">'; 
        } else {
          // If request is not successful, display an error message
          document.getElementById('imageContainer').innerHTML = '<p>Error: Failed to load image.</p>';
        }
      };
      xhr.send(formData);
    });
  </script>
</body>
</html>
""" 

def run_sim( base_infectivity, migration_fraction, seasonal_multiplier ):
    import sir_numpy_c as model
    import settings
    import demographics_settings as ds
    import report
    from tlc import run_simulation
    #ctx = model.initialize_database()
    #ctx = model.eula_init( ctx, ds.eula_age )

    #csv_writer = report.init()

    try:
        print( "Run sim" )
        subprocess.run(['/usr/local/bin/python3', 'tlc.py'], check=True) 
    except subprocess.CalledProcessError as e:
        # Handle subprocess error (e.g., log the error, restart the subprocess)
        print(f"Subprocess error: {e}")

def metrics_csv_to_json():
    import csv
    import json

    # Initialize an empty dictionary to store the data
    json_dict = {}

    # Open the CSV file and read its contents
    with open('metrics.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            key, value = row
            json_dict[key] = value
    return json_dict

def update_settings_file(key_value_pairs, filename="settings.py"):
    # Read the content of the settings file
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the line with the key to be replaced
    for i, line in enumerate(lines):
        for key, value in key_value_pairs.items():
            if line.startswith(f'{key}=') or line.startswith(f'{key} ='):
                # Replace the line with the new key-value pair
                lines[i] = f'{key}={value}\n'
                break

    # Write the updated content back to the file
    with open(filename, 'w') as file:
        file.writelines(lines)

    print( "Returning from run_sim." )

def update_settings( data ):
    # Read the settings.py file
    with open("settings.py", "r") as settings_file:
        lines = settings_file.readlines()

    # Parse each line and update the value if the key matches one of your variable names
    for i, line in enumerate(lines):
        # Split the line into key and value
        try:
            key, value = line.strip().split("=")
            # Check if the key matches one of your variable names
            # Can't find better way than this
            if key.strip() in data:
                print( f"Settings new value for {key}." )
                value = data[key.strip()]
                if key.strip() == "duration":
                    value += "*365"
                lines[i] = f"{key.strip()} = {value}\n" 
        except Exception as ex:
            print( str( ex ) )
            print( line )
            print( "Probably just a commment or blank line." )

    #print( "Saving new settings.py file as: " )
    #for line in lines:
        #print( line )
    # Write the updated key-value pairs back to the file
    with open("settings.py", "w") as settings_file:
        settings_file.writelines(lines)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        try:
            data = request.json
            if not data:
                raise ValueError("No JSON data provided")

            validate_params( data, params )

            # Extract and validate parameters
            base_infectivity = float(data.get('base_infectivity'))
            migration_fraction = float(data.get('migration_fraction'))
            seasonal_multiplier = float(data.get('seasonal_multiplier'))
            duration_years = int(data.get('duration'))

            # Translate duration from years to days
            duration_days = duration_years * 365

            # Prepare new key-value pairs
            new_kvps = {
                "base_infectivity": base_infectivity,
                "migration_fraction": migration_fraction,
                "seasonal_multiplier": seasonal_multiplier,
                "duration": duration_days
            }
            update_settings_file(new_kvps)
            run_sim(base_infectivity, migration_fraction, seasonal_multiplier)

            return metrics_csv_to_json()

        except (ValueError, TypeError) as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": "An unexpected error occurred: " + str(e)}), 500
    else: 
        # Return the API documentation
        api_doc = {
            "description": "API for submitting simulation parameters",
            "endpoints": {
                "/submit": {
                    "method": "POST",
                    "parameters": params,
                    "response": {
                        "status": "string",
                        "message": "string",
                        "url": "string (only if status is success)"
                    },
                    "errors": [
                        {"status": "error", "message": "No JSON data provided"},
                        {"status": "error", "message": "An unexpected error occurred: <error_message>"}
                    ]
                }
            }
        }

    return jsonify(api_doc) 

@app.route('/prevs.png')
def download_prevs():
    return send_file("./prevs.png", as_attachment=True)

@app.route('/')
def index():
    # Generate the HTML form with parameters
    # This could be dynamically generated based on the parameters your application expects
    form_html = render_template_string(FORM_TEMPLATE, params=params)
    return form_html

if __name__ == '__main__': 
    app.run(debug=False, host='0.0.0.0')
"""
    {% for param, desc in params.items() %}
      <label for="{{ param }}">{{ param }}:</label>
      <input type="text" name="{{ param }}" id="{{ param }}"><br>
      <small>{{ desc }}</small><br><br>
    {% endfor %}
"""
