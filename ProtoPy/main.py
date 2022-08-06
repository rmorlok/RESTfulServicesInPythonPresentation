#!/usr/bin/env python
import json

import webapp2

from google.appengine.ext import ndb

import protopy
from protopy import messages

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



class TeamMessage(messages.Message):
    id = messages.StringField()
    name = messages.StringField()
    colors = messages.StringField(repeated=True)
    mascot = messages.StringField()



class TeamsResponseMessage(messages.Message):
    teams = messages.MessageField(TeamMessage, repeated=True)



class PlayerMessage(messages.Message):
    id = messages.StringField()
    name = messages.StringField()
    position = messages.StringField()
    team_id = messages.StringField()



class PlayersResponseMessage(messages.Message):
    players = messages.MessageField(PlayerMessage, repeated=True)



def player_to_msg(player):
    return PlayerMessage(
        id=player.key.urlsafe() if player.key else None,
        name=player.name,
        position=player.position,
        team_id=player.team.urlsafe() if player.team else None
    )



def msg_to_player_set(msg, player=None):
    player = player or Player()

    player.name = msg.name
    player.position = msg.position

    team_id = msg.team_id
    if team_id:
        player.team = ndb.Key(urlsafe=team_id)

    return player



def msg_to_player_update(msg, player=None):
    player = player or Player()

    if msg.name is not None:
        player.name = msg.name

    if msg.position is not None:
        player.position = msg.position

    if msg.team_id is not None:
        team_id = msg.team_id
        player.team = ndb.Key(urlsafe=team_id)

    return player



def team_to_msg(team):
    return TeamMessage(
        id=team.key.urlsafe() if team.key else None,
        name=team.name,
        mascot=team.mascot,
        colors=team.colors
    )



def msg_to_team_set(msg, team=None):
    team = team or Team()

    team.name = msg.name
    team.mascot = msg.mascot
    team.colors = msg.colors

    return team



def msg_to_team_update(msg, team=None):
    team = team or Team()

    if msg.name is not None:
        team.name = msg.name

    if msg.mascot is not None:
        team.mascot = msg.mascot

    if msg.colors is not None:
        team.colors = msg.colors

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


    @protopy.endpoint
    def get_teams(self):
        response = TeamsResponseMessage()
        response.teams = []

        for team in Team.query().iter():
            response.teams.append(team_to_msg(team))

        return response



    @protopy.endpoint
    def get_team(self, team_id):
        return team_to_msg(get_team_or_404(team_id))



    @protopy.endpoint(team_details=TeamMessage)
    def create_team(self, team_details):
        team = msg_to_team_set(team_details)
        team.put()

        return 201, team_to_msg(team), {'Location': webapp2.uri_for('get_team', team_id=team.key.urlsafe())}



    @protopy.endpoint(team_details=TeamMessage)
    def set_team(self, team_id, team_details):
        team = get_team_or_404(team_id)
        team = msg_to_team_set(team_details, team=team)
        team.put()

        return team_to_msg(team)



    @protopy.endpoint(team_details=TeamMessage)
    def update_team(self, team_id, team_details):
        team = get_team_or_404(team_id)
        team = msg_to_team_update(team_details, team=team)
        team.put()

        return team_to_msg(team)



    @protopy.endpoint
    def delete_team(self, team_id):
        ndb.Key(urlsafe=team_id).delete()
        return 204



class PlayerHandler(webapp2.RequestHandler):


    @protopy.endpoint
    @protopy.query.string('position')
    def get_players(self, team_id, position):
        _ = get_team_or_404(team_id)
        response = PlayersResponseMessage()
        response.players = []

        q = Player.query(Player.team == ndb.Key(urlsafe=team_id))

        if position:
            q = q.filter(Player.position == position)

        for player in q.iter():
            response.players.append(player_to_msg(player))

        return response



    @protopy.endpoint
    def get_player(self, team_id, player_id):
        _ = get_team_or_404(team_id)
        return player_to_msg(get_player_or_404(player_id))



    @protopy.endpoint(player_details=PlayerMessage)
    def create_player(self, team_id, player_details):
        _ = get_team_or_404(team_id)
        player_details.team_id = team_id
        player = msg_to_player_set(player_details)
        player.put()

        return 201, player_to_msg(player), {'Location': webapp2.uri_for('get_player', team_id=team_id, player_id=player.key.urlsafe())}



    @protopy.endpoint(player_details=PlayerMessage)
    def set_player(self, team_id, player_id, player_details):
        _ = get_team_or_404(team_id)
        player = get_player_or_404(player_id)
        player = msg_to_player_set(player_details, player=player)
        player.put()

        return player_to_msg(player)



    @protopy.endpoint(player_details=PlayerMessage)
    def update_player(self, team_id, player_id, player_details):
        _ = get_team_or_404(team_id)
        player = get_player_or_404(player_id)
        player = msg_to_player_update(player_details, player=player)
        player.put()

        return player_to_msg(player)



    @protopy.endpoint
    def delete_player(self, team_id, player_id):
        _ = get_team_or_404(team_id)
        ndb.Key(urlsafe=player_id).delete()
        return 204



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