import a2s

return_dict = {}
address = ("45.91.103.47", 27165)
info = a2s.info(address, timeout=6)
rules = a2s.rules(address)
players = a2s.players(address)

print(info)
print("")
print(rules)
print("")
print(players)
print("#######################")


print(info.server_name)
print(info.player_count)

print(rules['NUMPUBCONN'])
