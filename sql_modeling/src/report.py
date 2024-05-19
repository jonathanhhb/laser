import csv
import numpy as np
import socket
from sparklines import sparklines
import pdb
import settings
import demographics_settings

write_report = True
publish_report = False
new_infections = np.zeros(len(demographics_settings.nodes), dtype=np.uint32)

# Configuration for the socket server
HOST = 'localhost'  # Use 'localhost' for local testing
PORT = 65432        # Port to bind the server to

client_sock = None

# Function to send CSV data over a socket
def send_csv_data(socket_conn, data):
    #csvwriter = csv.writer(socket_conn, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvwriter = csv.writer(socket_conn.makefile('w', newline=''), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in data:
        csvwriter.writerow(row)

def init():
    # Create a CSV file for reporting
    csvfile = open( settings.report_filename, 'w', newline='') 
    csvwriter = csv.writer(csvfile)
    #csvwriter.writerow(['Timestep', 'Node', 'Susceptible', 'Infected', 'New Infections', 'Recovered', 'Births', 'Deaths'])
    csvwriter.writerow(['Timestep', 'Node', 'Susceptible', 'Infected', 'New Infections', 'Recovered', 'Births'])
    if publish_report:
        global client_sock
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((HOST, PORT))
    return csvwriter

def write_timestep_report( csvwriter, timestep, infected_counts, susceptible_counts, recovered_counts, new_births, new_deaths ):
    # This function is model agnostic
    infecteds = np.array([infected_counts[key] for key in sorted(infected_counts.keys(), reverse=True)])
    total = {key: susceptible_counts.get(key, 0) + infected_counts.get(key, 0) + recovered_counts.get(key, 0) for key in susceptible_counts.keys()}
    totals = np.array([total[key] for key in sorted(total.keys(), reverse=True)])
    prev = infecteds/totals
    print( f"T={timestep}" )
    #print( list( sparklines( prev ) ) )
    # Write the counts to the CSV file
    #print( f"T={timestep},\nS={susceptible_counts},\nI={infected_counts},\nR={recovered_counts}" )
    if write_report:
        for node in demographics_settings.nodes:
            csvwriter.writerow([timestep,
                node,
                susceptible_counts[node] if node in susceptible_counts else 0,
                infected_counts[node] if node in infected_counts else 0,
                new_infections[node],
                recovered_counts[node] if node in recovered_counts else 0,
                new_births[node] if node in new_births else 0,
                #new_deaths[node] if node in new_deaths else 0,
                ]
            )

    if publish_report:
        data = []
        for node in demographics_settings.nodes:
            row = [
                timestep,
                node,
                susceptible_counts[node] if node in susceptible_counts else 0,
                infected_counts[node] if node in infected_counts else 0,
                new_infections[node],
                recovered_counts[node] if node in recovered_counts else 0,
                new_births[node] if node in new_births else 0,
                #new_deaths[node] if node in new_deaths else 0,
            ]
            data.append(row)
        send_csv_data( client_sock, data )
