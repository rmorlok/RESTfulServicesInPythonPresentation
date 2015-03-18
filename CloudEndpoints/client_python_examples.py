import json
import time

from apiclient.discovery import build

api_root = 'http://localhost:8080/_ah/api'
api = 'sports'
version = 'v1'
discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
service = build(api, version, discoveryServiceUrl=discovery_url)

#
# Create teams
#
gophers = service.teamsCreate(body={
        'name': 'Minnesota',
        'mascot': 'Gopher',
        'colors': ['maroon', 'gold']
    }).execute()

print "Gophers: " + json.dumps(gophers, indent=4)

badgers = service.teamsCreate(body={
        'name': 'Wisconsin',
        'mascot': 'Badger',
        'colors': ['cardinal', 'white']
    }).execute()

print "Badgers: " + json.dumps(badgers, indent=4)

# Let datastore settle
time.sleep(0.2)

#
# Get teams
#
print json.dumps(service.teamsList().execute(), indent=4)

#
# Get team
#
print "Gophers:" + json.dumps(service.teamsGet(team_id=gophers['id']).execute(), indent=4)

#
# Update team
#
badgers = service.teamsSet(team_id=badgers['id'], body={
        'name': 'Wisconsin',
        'mascot': 'Bucky Badger',
        'colors': ['cardinal', 'white']
    }).execute()

print "Updated Badgers: " + json.dumps(badgers, indent=4)

#
# Incrementally update team
#
gophers = service.teamsUpdate(team_id=gophers['id'], body={'mascot': 'Goldy Gopher'}).execute()

print "Updated Gophers: " + json.dumps(gophers, indent=4)

#
# Delete team
#
print "Delete Badgers"
service.teamsDelete(team_id=badgers['id']).execute()

#
# Create players
#
kyle_rau = service.playersCreate(url_team_id=gophers['id'], body={
        'name': 'Kyle Rau',
        'position': 'Forward'
    }).execute()

print "Kyle Rau: " + json.dumps(kyle_rau, indent=4)

adam_wilcox = service.playersCreate(url_team_id=gophers['id'], body={
        'name': 'Adam Wilcox',
        'position': 'Goalie'
    }).execute()

print "Adam Wilcox: " + json.dumps(adam_wilcox, indent=4)

# Let datastore settle
time.sleep(0.2)

#
# Get players
#
print "Gopher Players: " + json.dumps(service.playersList(url_team_id=gophers['id']).execute(), indent=4)

#
# Get players for a specific position
#
print "Gopher Forwards: " + json.dumps(service.playersList(url_team_id=gophers['id'], position='Forward').execute(), indent=4)

#
# Get player
#
print "Kyle Rau: " + json.dumps(service.playersGet(url_team_id=gophers['id'], url_player_id=kyle_rau['id']).execute(), indent=4)

#
# Update player
#
kyle_rau = service.playersSet(url_team_id=gophers['id'], url_player_id=kyle_rau['id'], body={
        'name': 'Kyle Rau',
        'position': 'Defense',
    }).execute()

print "Updated Kyle Rau: " + json.dumps(kyle_rau, indent=4)

#
# Incrementally update player
#
adam_wilcox = service.playersUpdate(url_team_id=gophers['id'], url_player_id=adam_wilcox['id'], body={'position': 'Forward'}).execute()

print "Updated Adam Wilcox: " + json.dumps(adam_wilcox, indent=4)

#
# Delete player
#
print "Delete Player"
service.playersDelete(url_team_id=gophers['id'], url_player_id=adam_wilcox['id']).execute()