import threading
from ping3 import ping
from influxdb import InfluxDBClient
import time
import yaml
import os
import sys
from dotenv import load_dotenv

# use dotenv to load environment variables from .env file
if os.path.exists(".env"):
    load_dotenv()

# load environment variables
def get_required_env_variables(var_names):
    env_vars = {}
    for var_name in var_names:
        try:
            env_vars[var_name] = os.environ[var_name]
        except KeyError:
            raise ValueError(f"Required environment variable '{var_name}' is not set.")
    return env_vars

# get required environment variables
try:
    env_vars = get_required_env_variables(['INFLUX_HOST', 'INFLUX_PORT', 'INFLUX_DB'])
    print("Loaded environment variables:", env_vars)
except ValueError as e:
    print("Error:", str(e))
    sys.exit(1)


# measure ping and write to influxdb
def measure(ip, name):
    host = env_vars['INFLUX_HOST']
    port = env_vars['INFLUX_PORT']
    database = env_vars['INFLUX_DB'] 

    client = InfluxDBClient(host=host, port=port)
    client.switch_database(database)

    response_time = ping(ip)

    if response_time is not None:
        print(f"Response time: {ip} {response_time} ms")
    else:
        print("Ping request timed out")

    measurement = 'ping' 
    tags = {'name': name}

    fields = {'response_time': response_time}


    data = [
        {
            "measurement": measurement,
            "tags": tags,
            "fields": fields
        }
    ]


    client.write_points(data)

    client.close()


# main loop
while True:
    with open('ping.yml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    devices = yaml_data['devices']
    
    threads = []
    for device in devices:
        name = device['name']
        ip = device['ip']
        thread = threading.Thread(target=measure, args=(ip, name))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
        
    print("Thread has finished")
    time.sleep(1)
