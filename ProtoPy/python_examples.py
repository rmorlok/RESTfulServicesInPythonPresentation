#!/usr/bin/env python
import requests
import json
import time

host = "http://localhost:8080"

#
# Create teams
#
gophers = json.loads(requests.post(
    url=host + "/v1/teams",
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({
        'name': 'Minnesota',
        'mascot': 'Gopher',
        'colors': ['maroon', 'gold']
    })
).content)

print "Gophers: " + json.dumps(gophers, indent=4)

badgers = json.loads(requests.post(
    url=host + "/v1/teams",
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({
        'name': 'Wisconsin',
        'mascot': 'Badger',
        'colors': ['cardinal', 'white']
    })
).content)

print "Badgers: " + json.dumps(badgers, indent=4)

# Let datastore settle
time.sleep(0.2)

#
# Get teams
#
print json.dumps(json.loads(requests.get(
    url=host + "/v1/teams",
    headers={'Accept': 'application/json'}).content), indent=4)

#
# Get team
#
print "Gophers:" + json.dumps(json.loads(requests.get(
    url=host + "/v1/teams/" + gophers['id'],
    headers={'Accept': 'application/json'}).content), indent=4)

#
# Update team
#
badgers = json.loads(requests.put(
    url=host + "/v1/teams/" + badgers['id'],
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({
        'name': 'Wisconsin',
        'mascot': 'Bucky Badger',
        'colors': ['cardinal', 'white']
    })
).content)

print "Updated Badgers: " + json.dumps(badgers, indent=4)

#
# Incrementally update team
#
gophers = json.loads(requests.patch(
    url=host + "/v1/teams/" + gophers['id'],
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({'mascot': 'Goldy Gopher'})
).content)

print "Updated Gophers: " + json.dumps(gophers, indent=4)

#
# Delete team
#
print "Delete Status: %d" % requests.delete(url=host + "/v1/teams/" + badgers['id']).status_code

#
# Create players
#
kyle_rau = json.loads(requests.post(
    url=host + "/v1/teams/%s/players" % gophers['id'],
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({
        'name': 'Kyle Rau',
        'position': 'Forward'
    })
).content)

print "Kyle Rau: " + json.dumps(kyle_rau, indent=4)

adam_wilcox = json.loads(requests.post(
    url=host + "/v1/teams/%s/players" % gophers['id'],
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({
        'name': 'Adam Wilcox',
        'position': 'Goalie'
    })
).content)

print "Adam Wilcox: " + json.dumps(adam_wilcox, indent=4)

# Let datastore settle
time.sleep(0.2)

#
# Get players
#
print "Gopher Players: " + json.dumps(json.loads(requests.get(
    url=host + "/v1/teams/%s/players" % gophers['id'],
    headers={'Accept': 'application/json'}).content), indent=4)

#
# Get players for a specific position
#
print "Gopher Forwards: " + json.dumps(json.loads(requests.get(
    url=host + "/v1/teams/%s/players" % gophers['id'],
    headers={'Accept': 'application/json'},
    params={'position': 'Forward'}).content), indent=4)

#
# Get player
#
print "Kyle Rau: " + json.dumps(json.loads(requests.get(
    url=host + "/v1/teams/%s/players/%s" % (gophers['id'], kyle_rau['id']),
    headers={'Accept': 'application/json'}).content), indent=4)

#
# Update player
#
kyle_rau = json.loads(requests.put(
    url=host + "/v1/teams/%s/players/%s" % (gophers['id'], kyle_rau['id']),
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({
        'name': 'Kyle Rau',
        'position': 'Defense',
    })
).content)

print "Updated Kyle Rau: " + json.dumps(kyle_rau, indent=4)

#
# Incrementally update player
#
adam_wilcox = json.loads(requests.patch(
    url=host + "/v1/teams/%s/players/%s" % (gophers['id'], adam_wilcox['id']),
    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
    data=json.dumps({'position': 'Forward'})
).content)

print "Updated Adam Wilcox: " + json.dumps(adam_wilcox, indent=4)

#
# Delete player
#
print "Delete Status: %d" % requests.delete(url=host + "/v1/teams/%s/players/%s" % (gophers['id'], adam_wilcox['id'])).status_code