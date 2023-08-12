import a2s
import yaml
from concurrent.futures import ThreadPoolExecutor
import os
import sys
from dotenv import load_dotenv
from influxdb import InfluxDBClient
import time

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


def a2s_info(host):
    return_dict = {}
    address = (host, 27165)
    info = a2s.info(address, timeout=6)
    rules = a2s.rules(address)
    players = a2s.players(address)
    
    #print(info)
    #print("")
    #print(rules)
    #print("")
    #print(players)
    #print("#######################")

    #for player in players:
        #print(player.name)
    return_dict['server_name'] = info.server_name
    return_dict['player_count'] = info.player_count
    return return_dict

def influx_write(name, player_count):
    host = env_vars['INFLUX_HOST']
    port = env_vars['INFLUX_PORT']
    database = env_vars['INFLUX_DB'] 

    client = InfluxDBClient(host=host, port=port)
    client.switch_database(database)

    measurement = 'squad_player_count' 
    tags = {'name': name}

    fields = {'player_count': player_count}

    data = [
        {
            "measurement": measurement,
            "tags": tags,
            "fields": fields
        }
    ]

    client.write_points(data)

    client.close()

if __name__ == "__main__":

    with open('squad.yml', 'r') as file:
        yaml_data = yaml.safe_load(file)


    while True:
        devices = yaml_data['devices']

        squad_data = []

        print("Squad: Thread")
        with ThreadPoolExecutor(max_workers=5) as executor:
            for device in devices:
                thread_return = executor.submit(a2s_info, device['ip'])
                tmp_dict = thread_return.result()
                tmp_dict['name'] = device['name']
                squad_data.append(tmp_dict)

        print("Squad: Influx")
        for data in squad_data:
            # print(f"{data['name']}: {data['player_count']}")
            influx_write(data['name'], data['player_count'])
            
        time.sleep(30)
