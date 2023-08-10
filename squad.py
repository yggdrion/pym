import a2s
import yaml
from concurrent.futures import ThreadPoolExecutor


def a2s_info(host):
    address = (host, 27165)
    info = a2s.info(address)
    rules = a2s.rules(address)
    players = a2s.players(address)
    
    print(info)
    print("")
    print(rules)
    print("")
    print(players)
    print("#######################")

    for player in players:
        print(player.name)
    return info.server_name

if __name__ == "__main__":

    with open('squad.yml', 'r') as file:
        yaml_data = yaml.safe_load(file)

    devices = yaml_data['devices']

    squad_data = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        for device in devices:
            return_dict = executor.submit(a2s_info, device['ip'])
            squad_data.append(return_dict.result())


    print("")

    for data in squad_data:
        print(data)
