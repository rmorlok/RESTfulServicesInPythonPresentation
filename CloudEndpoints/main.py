import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import ndb


class Team(ndb.Model):
    name = ndb.StringProperty()
    colors = ndb.StringProperty(repeated=True)
    mascot = ndb.StringProperty()


class Player(ndb.Model):
    team = ndb.KeyProperty()
    name = ndb.StringProperty()
    position = ndb.StringProperty()


class TeamMessage(messages.Message):
    id = messages.StringField(1)
    name = messages.StringField(2)
    colors = messages.StringField(3, repeated=True)
    mascot = messages.StringField(4)


TEAM_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    team_id=messages.StringField(2, required=True))

TEAM_UPDATE = endpoints.ResourceContainer(
    TeamMessage,
    team_id=messages.StringField(2, required=True))


class TeamsResponseMessage(messages.Message):
    teams = messages.MessageField(TeamMessage, 1, repeated=True)


class PlayerMessage(messages.Message):
    id = messages.StringField(1)
    name = messages.StringField(2)
    position = messages.StringField(3)
    team_id = messages.StringField(4)


class PlayersResponseMessage(messages.Message):
    players = messages.MessageField(PlayerMessage, 1, repeated=True)


class PlayersRequestMessage(messages.MessageField):
    position = messages.StringField(1)

PLAYERS_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    url_team_id=messages.StringField(2, required=True),
    position=messages.StringField(3))

PLAYER_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,
    url_team_id=messages.StringField(2, required=True),
    url_player_id=messages.StringField(3, required=True))

PLAYER_CREATE = endpoints.ResourceContainer(
    PlayerMessage,
    url_team_id=messages.StringField(2, required=True))

PLAYER_UPDATE = endpoints.ResourceContainer(
    PlayerMessage,
    url_team_id=messages.StringField(2, required=True),
    url_player_id=messages.StringField(3, required=True))


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
        raise endpoints.NotFoundException()

    if not isinstance(t, Team):
        raise endpoints.NotFoundException()

    return t


def get_player_or_404(player_id):
    p = ndb.Key(urlsafe=player_id).get()

    if not p:
        raise endpoints.NotFoundException()

    if not isinstance(p, Player):
        raise endpoints.NotFoundException()

    return p


@endpoints.api(name='sports',
               version='v1',
               description='Sports API')
class SportsAPI(remote.Service):
    @endpoints.method(message_types.VoidMessage,
                      TeamsResponseMessage,
                      name='teamsList',
                      path='teams',
                      http_method='GET')
    def get_teams(self, request):
        response = TeamsResponseMessage()
        response.teams = []

        for team in Team.query().iter():
            response.teams.append(team_to_msg(team))

        return response

    @endpoints.method(TEAM_REQUEST,
                      TeamMessage,
                      name='teamsGet',
                      path='teams/{team_id}',
                      http_method='GET')
    def get_team(self, request):
        return team_to_msg(get_team_or_404(request.team_id))


    @endpoints.method(TeamMessage,
                      TeamMessage,
                      name='teamsCreate',
                      path='teams',
                      http_method='POST')
    def create_team(self, request):
        team = msg_to_team_set(request)
        team.put()

        return team_to_msg(team)

    @endpoints.method(TEAM_UPDATE,
                      TeamMessage,
                      name='teamsSet',
                      path='teams/{team_id}',
                      http_method='PUT')
    def set_team(self, request):
        team = get_team_or_404(request.team_id)
        team = msg_to_team_set(request, team=team)
        team.put()

        return team_to_msg(team)

    @endpoints.method(TEAM_UPDATE,
                      TeamMessage,
                      name='teamsUpdate',
                      path='teams/{team_id}',
                      http_method='PATCH')
    def update_team(self, request):
        team = get_team_or_404(request.team_id)
        team = msg_to_team_update(request, team=team)
        team.put()

        return team_to_msg(team)

    @endpoints.method(TEAM_REQUEST,
                      message_types.VoidMessage,
                      name='teamsDelete',
                      path='teams/{team_id}',
                      http_method='DELETE')
    def delete_team(self, request):
        ndb.Key(urlsafe=request.team_id).delete()
        return message_types.VoidMessage()

    @endpoints.method(PLAYERS_REQUEST,
                      PlayersResponseMessage,
                      name='playersList',
                      path='teams/{url_team_id}/players',
                      http_method='GET')
    def get_players(self, request):
        _ = get_team_or_404(request.url_team_id)
        response = PlayersResponseMessage()
        response.players = []

        q = Player.query(Player.team == ndb.Key(urlsafe=request.url_team_id))

        if request.position:
            q = q.filter(Player.position == request.position)

        for player in q.iter():
            response.players.append(player_to_msg(player))

        return response

    @endpoints.method(PLAYER_REQUEST,
                      PlayerMessage,
                      name='playersGet',
                      path='teams/{url_team_id}/players/{url_player_id}',
                      http_method='GET')
    def get_player(self, request):
        _ = get_team_or_404(request.url_team_id)
        return player_to_msg(get_player_or_404(request.url_player_id))


    @endpoints.method(PLAYER_CREATE,
                      PlayerMessage,
                      name='playersCreate',
                      path='teams/{url_team_id}/players',
                      http_method='POST')
    def create_player(self, request):
        _ = get_team_or_404(request.url_team_id)
        request.team_id = request.url_team_id
        player = msg_to_player_set(request)
        player.put()

        return player_to_msg(player)

    @endpoints.method(PLAYER_UPDATE,
                      PlayerMessage,
                      name='playersSet',
                      path='teams/{url_team_id}/players/{url_player_id}',
                      http_method='PUT')
    def set_player(self, request):
        _ = get_team_or_404(request.url_team_id)
        player = get_player_or_404(request.url_player_id)
        player = msg_to_player_set(request, player=player)
        player.put()

        return player_to_msg(player)

    @endpoints.method(PLAYER_UPDATE,
                      PlayerMessage,
                      name='playersUpdate',
                      path='teams/{url_team_id}/players/{url_player_id}',
                      http_method='PATCH')
    def update_player(self, request):
        _ = get_team_or_404(request.url_team_id)
        player = get_player_or_404(request.url_player_id)
        player = msg_to_player_update(request, player=player)
        player.put()

        return player_to_msg(player)

    @endpoints.method(PLAYER_REQUEST,
                      message_types.VoidMessage,
                      name='playersDelete',
                      path='teams/{url_team_id}/players/{url_player_id}',
                      http_method='DELETE')
    def delete_player(self, request):
        _ = get_team_or_404(request.url_team_id)
        ndb.Key(urlsafe=request.url_player_id).delete()
        return message_types.VoidMessage()



app = endpoints.api_server([SportsAPI])