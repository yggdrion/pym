from influxdb import InfluxDBClient
import sys
import os
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

def write(measurement: str, tags: dict, fields: dict) -> None:
    """
    Write data to InfluxDB.
    Args:
        measurement (str): the table: 'squad_player_count'
        tags (dict): the tags: {'name': name, 'ip': ip}
        fields (dict): A dictionary of fields: {'player_count': player_count} 
    Returns:
        None
    """
    
    host = env_vars['INFLUX_HOST']
    port = env_vars['INFLUX_PORT']
    database = env_vars['INFLUX_DB'] 
    database = 'test'
    
    print(f"Writing data measurement={measurement} tags={tags} fields={fields} to InfluxDB at {host}:{port} database={database}")

    client = InfluxDBClient(host=host, port=port)
    client.switch_database(database)


    data = [
        {
            "measurement": measurement,
            "tags": tags,
            "fields": fields
        }
    ]

    client.write_points(data)
    client.close()
