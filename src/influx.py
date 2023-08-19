from influxdb import InfluxDBClient
import sys
import os
from dotenv import load_dotenv
from src import env

try:
    env_vars = env.get_required_env_variables(['INFLUX_HOST', 'INFLUX_PORT', 'INFLUX_DB'])
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
    database = 'data'

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
