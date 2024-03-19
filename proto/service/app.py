from flask import Flask, request, render_template_string, send_file
import subprocess

app = Flask(__name__)

params = [
{
        'name': 'nodes',
	'default': "32",
        'description': "Number of nodes/populations"
},
{
        'name': 'ticks',
	'default': "10",
        'description': "Simulation duration in years."
},
{
        'name': 'exp_mean',
	'default': "4",
        'description': "exp_mean?"
},
{ 
        'name': 'exp_std',
	'default': "1",
        'description': "exp_std?"
},
{ 
        'name': 'inf_mean',
	'default': "5",
        'description': "infectiousness mean?"
},
{
        'name': 'inf_std',
	'default': "1",
        'description': "infectiousness standard deviation"
},
{
        'name': 'r_naught',
	'default': "2.5",
        'description': "Reproductive number"
},
{
        'name': 'seed',
	'default': "20240227",
        'description': "Random number seed"
}, 
]


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
        if (xhr.status == 200) {
          // Remove spinner
          overlay.style.display = 'none';
          spinner.style.display = 'none';
          
          // If request is successful, display the returned image
          var timestamp = new Date().getTime(); // Generate a timestamp
          var imageUrl = 'prevs.png?' + timestamp; // Append timestamp to image URL
          document.getElementById('imageContainer').innerHTML = '<img src="' + imageUrl + '" alt="prevs" style="max-width: 100%;">'; 
        } else {
          // If request is not successful, display an error message
          document.getElementById('imageContainer').innerHTML = '<p>Error: Failed to load image.</p>' + '<p>' + xhr.status + '</p>';
        }
      };
      xhr.send(formData);
    });
  </script>
</body>
</html>
"""

def run_sim( params_array ): 
    # Run the simulation for 1000 timesteps
    try:
        print( "Run sim" )
        app_cmd = ['/usr/local/bin/python3', 'engwal.py' ]
        app_cmd.extend( params_array )
        subprocess.run( app_cmd, check=True) 
    except subprocess.CalledProcessError as e:
        # Handle subprocess error (e.g., log the error, restart the subprocess)
        print(f"Subprocess error: {e}")
    print( "Returning from run_sim." )

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        # Process the submitted parameters
        data = request.form
        # Run your application logic here
        #base_infectivity = float(data['base_infectivity'])
        #cbr = int(data['cbr'])
        ticks = int(data['ticks'])
        def get_params( data ):
            result_array = []

            # Iterate over the keys of the dictionary
            for key in data:
                result_array.append( '--' + key )

                # Retrieve the associated values
                values = str(data[key])
                result_array.append( values )
                
            print( f"result_array = {result_array}." )
            return result_array
        # Parse settings and run.
        params_array = get_params( data )

        print( f"run_sim called with {params_array}" )
        run_sim( params_array ) 
        
        print( "Sim completed. Returning output plot URL." )
        return {'url': '/inf.png'}
    else:
        # Return the API documentation
        return API_DOC

@app.route('/prevs.png', methods=['GET'])
def download_prevs():
    return send_file("/app/inf.png", as_attachment=True)

@app.route('/')
def index():
    # Generate the HTML form with parameters
    # This could be dynamically generated based on the parameters your application expects
    form_html = render_template_string(FORM_TEMPLATE, params=params)
    return form_html

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0')
"""
    {% for param, desc in params.items() %}
      <label for="{{ param }}">{{ param }}:</label>
      <input type="text" name="{{ param }}" id="{{ param }}"><br>
      <small>{{ desc }}</small><br><br>
    {% endfor %}
"""
