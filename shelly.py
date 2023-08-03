import requests
import socket
from concurrent.futures import ThreadPoolExecutor
import time
from influxdb import InfluxDBClient
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
    env_vars = get_required_env_variables(['INFLUX_HOST', 'INFLUX_PORT', 'INFLUX_DB', 'IP_PREFIX'])
    print("Loaded environment variables:", env_vars)
except ValueError as e:
    print("Error:", str(e))
    sys.exit(1)

def is_webserver_running(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((ip, 80))
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def check_valid_json(response):
    try:
        _ = response.json()
        return True
    except ValueError:
        return False


def get_json_data(ip):
    return_dict = {}

    response_json_status = requests.get(f"http://{ip}/status")
    response_json_settings = requests.get(f"http://{ip}/settings")
    try:
        # print(response_json_status.json()["meters"][0]["power"])
        # print(response_json_settings.json()["name"])
        return_dict["ip"] = ip
        return_dict["power"] = response_json_status.json()["meters"][0]["power"]
        return_dict["name"] = response_json_settings.json()["name"]
        return return_dict
    except (KeyError, IndexError):
        return None
    

def scan_ip(ip_address, web_servers):
    if is_webserver_running(ip_address):
        url = f"http://{ip_address}/status"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            if check_valid_json(response):
                web_servers.append(ip_address)
        except Exception as e:
            print(f"Error while scanning {ip_address}: {e}")

def scan_local_network():
    network_prefix = env_vars['IP_PREFIX']
    web_servers = []

    with ThreadPoolExecutor(max_workers=30) as executor:
        for host in range(1, 255):
            ip_address = network_prefix + str(host)
            executor.submit(scan_ip, ip_address, web_servers)

    return web_servers

def write_to_influx(list):
    host = env_vars['INFLUX_HOST']
    port = env_vars['INFLUX_PORT']
    database = env_vars['INFLUX_DB']

    client = InfluxDBClient(host=host, port=port)
    client.switch_database(database)


    for i in list:
        tags = {'name': i["name"], 'ip': i["ip"]}
        fields = {'power': i["power"]}
        data = [
            {
                "measurement": "power",
                "tags": tags,
                "fields": fields
            }
        ]

        client.write_points(data)
    client.close()


if __name__ == "__main__":
    web_servers = scan_local_network()


    while True:
        # watt_usage = {}
        power_list = []
        with ThreadPoolExecutor(max_workers=5) as executor2:
            for web_server in web_servers:
                return_dict = executor2.submit(get_json_data, web_server)
                #print(return_dict.result())
                power_list.append(return_dict.result())

        for i in power_list:
            print(i)
        write_to_influx(power_list)
        time.sleep(1)
