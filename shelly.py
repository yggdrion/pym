import requests
import socket
from concurrent.futures import ThreadPoolExecutor
import time
from src import influx
from src import env  

env_vars = env.get_required_env_variables(['IP_PREFIX'])

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

if __name__ == "__main__":
    web_servers = scan_local_network()


    while True:
        print("Shelly: Thread")
        power_list = []
        with ThreadPoolExecutor(max_workers=5) as executor2:
            for web_server in web_servers:
                return_dict = executor2.submit(get_json_data, web_server)
                #print(return_dict.result())
                power_list.append(return_dict.result())

        print("Shelly: Influx")
        for shelly in power_list:
            influx.write('shelly', {'name': shelly["name"], 'ip': shelly["ip"]}, {'power': shelly["power"]})
        time.sleep(5)
