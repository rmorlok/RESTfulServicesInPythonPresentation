#!/usr/bin/env python
import json

import webapp2

from google.appengine.ext import ndb

# Monkey patch Webapp2 to support PATCH
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods


class Team(ndb.Model):
    name = ndb.StringProperty()
    colors = ndb.StringProperty(repeated=True)
    mascot = ndb.StringProperty()


class Player(ndb.Model):
    team = ndb.KeyProperty()
    name = ndb.StringProperty()
    position = ndb.StringProperty()


def player_to_dict(player):
    return {
        'id': player.key.urlsafe() if player.key else None,
        'name': player.name,
        'position': player.position,
        'team_id': player.team.urlsafe() if player.team else None
    }


def dict_to_player_set(d, player=None):
    player = player or Player()

    player.name = d.get('name', None)
    player.position = d.get('position', None)

    team_id = d.get('team_id', None)
    if team_id:
        player.team = ndb.Key(urlsafe=team_id)

    return player


def dict_to_player_update(d, player=None):
    player = player or Player()

    if 'name' in d:
        player.name = d['name']

    if 'position' in d:
        player.position = d['position']

    if 'team_id' in d:
        team_id = d['team_id']
        player.team = ndb.Key(urlsafe=team_id)

    return player


def team_to_dict(team):
    d = team.to_dict()
    d['id'] = team.key.urlsafe() if team.key else None
    return d


def dict_to_team_set(d, team=None):
    team = team or Team()

    team.name = d.get('name', None)
    team.mascot = d.get('mascot', None)
    team.colors = d.get('colors', [])

    return team


def dict_to_team_update(d, team=None):
    team = team or Team()

    if 'name' in d:
        team.name = d['name']

    if 'mascot' in d:
        team.mascot = d['mascot']

    if 'colors' in d:
        team.colors = d['colors']

    return team


def get_team_or_404(team_id):
    t = ndb.Key(urlsafe=team_id).get()

    if not t:
        raise webapp2.exc.HTTPNotFound()

    if not isinstance(t, Team):
        raise webapp2.exc.HTTPNotFound()

    return t


def get_player_or_404(player_id):
    p = ndb.Key(urlsafe=player_id).get()

    if not p:
        raise webapp2.exc.HTTPNotFound()

    if not isinstance(p, Player):
        raise webapp2.exc.HTTPNotFound()

    return p


class TeamHandler(webapp2.RequestHandler):
    def get_teams(self):
        team_dicts = []

        for team in Team.query().iter():
            team_dicts.append(team_to_dict(team))

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(team_dicts))

    def create_team(self):
        team = None
        try:
            team_dict = json.loads(self.request.body)
            team = dict_to_team_set(team_dict)
            team.put()
        except:
            raise webapp2.exc.HTTPBadRequest()

        self.response.headers['Location'] = webapp2.uri_for('get_team', team_id=team.key.urlsafe())
        self.response.status_int = 201
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(team_to_dict(team)))

    def get_team(self, team_id):
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(team_to_dict(get_team_or_404(team_id))))

    def set_team(self, team_id):
        team = get_team_or_404(team_id)

        try:
            team_dict = json.loads(self.request.body)
            team = dict_to_team_set(team_dict, team=team)
            team.put()
        except:
            raise webapp2.exc.HTTPBadRequest()

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(team_to_dict(team)))

    def update_team(self, team_id):
        team = get_team_or_404(team_id)

        try:
            team_dict = json.loads(self.request.body)
            team = dict_to_team_update(team_dict, team=team)
            team.put()
        except:
            raise webapp2.exc.HTTPBadRequest()

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(team_to_dict(team)))

    def delete_team(self, team_id):
        team_key = ndb.Key(urlsafe=team_id)
        ndb.delete_multi([key for key in Player.query(Player.team == team_key).iter(keys_only=True)])
        team_key.delete()
        self.response.status_int = 204


class PlayerHandler(webapp2.RequestHandler):
    def get_players(self, team_id):
        _ = get_team_or_404(team_id)
        player_dicts = []

        q = Player.query(Player.team == ndb.Key(urlsafe=team_id))

        if 'position' in self.request.GET:
            q = q.filter(Player.position == self.request.GET['position'])

        for player in q.iter():
            player_dicts.append(player_to_dict(player))

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(player_dicts))

    def create_player(self, team_id):
        team = get_team_or_404(team_id)
        player = None
        try:
            player_dict = json.loads(self.request.body)
            player_dict['team_id'] = team_id
            player = dict_to_player_set(player_dict)
            player.put()
        except:
            raise webapp2.exc.HTTPBadRequest()

        self.response.headers['Location'] = webapp2.uri_for('get_player', team_id=team.key.urlsafe(), player_id=player.key.urlsafe())
        self.response.status_int = 201
        self.response.content_type = 'application/json'
        self.response.write(json.dumps(player_to_dict(player)))

    def get_player(self, team_id, player_id):
        team = get_team_or_404(team_id)
        player = get_player_or_404(player_id)

        if player.team != team.key:
            raise webapp2.exc.HTTPNotFound()

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(player_to_dict(player)))

    def set_player(self, team_id, player_id):
        team = get_team_or_404(team_id)
        player = get_player_or_404(player_id)

        if player.team != team.key:
            raise webapp2.exc.HTTPNotFound()

        try:
            player_dict = json.loads(self.request.body)
            player = dict_to_player_set(player_dict, player=player)
            player.put()
        except:
            raise webapp2.exc.HTTPBadRequest()

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(player_to_dict(player)))

    def update_player(self, team_id, player_id):
        team = get_team_or_404(team_id)
        player = get_player_or_404(player_id)

        if player.team != team.key:
            raise webapp2.exc.HTTPNotFound()

        try:
            player_dict = json.loads(self.request.body)
            player = dict_to_player_update(player_dict, player=player)
            player.put()
        except:
            raise webapp2.exc.HTTPBadRequest()

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(player_to_dict(player)))

    def delete_player(self, team_id, player_id):
        _ = get_team_or_404(team_id)
        ndb.Key(urlsafe=player_id).delete()
        self.response.status_int = 204

app = webapp2.WSGIApplication([
    webapp2.Route(r'/v1/teams',                               methods=['GET'],    handler='main.TeamHandler:get_teams',       name='get_teams'),
    webapp2.Route(r'/v1/teams',                               methods=['POST'],   handler='main.TeamHandler:create_team',     name='create_team'),
    webapp2.Route(r'/v1/teams/<team_id>',                     methods=['GET'],    handler='main.TeamHandler:get_team',        name='get_team'),
    webapp2.Route(r'/v1/teams/<team_id>',                     methods=['PUT'],    handler='main.TeamHandler:set_team',        name='set_team'),
    webapp2.Route(r'/v1/teams/<team_id>',                     methods=['PATCH'],  handler='main.TeamHandler:update_team',     name='update_team'),
    webapp2.Route(r'/v1/teams/<team_id>',                     methods=['DELETE'], handler='main.TeamHandler:delete_team',     name='delete_team'),
    webapp2.Route(r'/v1/teams/<team_id>/players',             methods=['GET'],    handler='main.PlayerHandler:get_players',   name='get_players'),
    webapp2.Route(r'/v1/teams/<team_id>/players',             methods=['POST'],   handler='main.PlayerHandler:create_player', name='create_player'),
    webapp2.Route(r'/v1/teams/<team_id>/players/<player_id>', methods=['GET'],    handler='main.PlayerHandler:get_player',    name='get_player'),
    webapp2.Route(r'/v1/teams/<team_id>/players/<player_id>', methods=['PUT'],    handler='main.PlayerHandler:set_player',    name='set_player'),
    webapp2.Route(r'/v1/teams/<team_id>/players/<player_id>', methods=['PATCH'],  handler='main.PlayerHandler:update_player', name='update_player'),
    webapp2.Route(r'/v1/teams/<team_id>/players/<player_id>', methods=['DELETE'], handler='main.PlayerHandler:delete_player', name='delete_player')
], debug=True)
