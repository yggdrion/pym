import a2s
import yaml
from concurrent.futures import ThreadPoolExecutor
import time
from src import influx

def a2s_info(name, host, port):
    return_dict = {}
    try:
        #print(f"Getting info for {name} - {host}:{port}")
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

        return_dict['name'] = name
        return_dict['server_name'] = info.server_name
        return_dict['player_count'] = info.player_count
        return_dict['map_name'] = info.map_name
        return_dict['game_mode'] = rules['GameMode_s']
        return_dict['team_one'] = rules['TeamOne_s']
        return_dict['team_two'] = rules['TeamTwo_s']
        
        # for i in return_dict:
        #     print(f"{i}: {return_dict[i]}")
        # print("#######################")        

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
                thread_return = executor.submit(a2s_info, server['name'], server['ip'], server['port'])
                if thread_return.result() is None:
                    print(f"Error: {server['name']}")
                    continue
                squad_data.append(thread_return.result())

        print("Squad: Influx")
        for data in squad_data:
            #print(data)
            measurement = 'squad'
            tags = {'name': data['name']}
            fields = {'player_count': data['player_count']}
            influx.write(measurement, tags, fields)
            
        time.sleep(30)
