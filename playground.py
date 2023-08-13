from src import influx

measurement = 'test'
tags = {'name': 'test'}
fields = {'player_count': 1}


influx.write(measurement, tags, fields)
