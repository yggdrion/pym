import a2s
import yaml
from concurrent.futures import ThreadPoolExecutor
import time
from src import influx

def a2s_info(host, port):
    return_dict = {}
    try:
        address = (host, port)
        info = a2s.info(address, timeout=10)
        # print(f"Got info for {host}:{port}")
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
    
    except:
        return None



if __name__ == "__main__":

    with open('squad.yml', 'r') as file:
        yaml_data = yaml.safe_load(file)


    while True:
        server_list = yaml_data['devices']

        squad_data = []

        print("Squad: Thread")
        with ThreadPoolExecutor(max_workers=3) as executor:
            for server in server_list:
                thread_return = executor.submit(a2s_info, server['ip'], server['port'])
                if thread_return.result() is None:
                    print(f"Error: {server['name']}")
                    continue
                tmp_dict = thread_return.result()
                tmp_dict['name'] = server['name']
                squad_data.append(tmp_dict)

        print("Squad: Influx")
        for data in squad_data:
            #print(data)
            influx.write('squad', {'name': data['name']}, {'player_count': data['player_count']})
            
        time.sleep(30)
