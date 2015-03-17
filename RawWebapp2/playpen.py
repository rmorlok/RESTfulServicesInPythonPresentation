import os
import unittest
import random
import logging
import json

from webapp2_extras import jinja2

from google.appengine.ext import testbed
from google.appengine.api import apiproxy_stub_map
from google.appengine.datastore import datastore_stub_util

import main


class SomeTest(unittest.TestCase):
    def setUp(self):
        super(SomeTest, self).setUp()

        # Activate the testbed, which prepares the service stubs for use.
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        # Restore original environment variables
        self.testbed.deactivate()

        super(SomeTest, self).tearDown()

    def test_to_dict(self):
        t = main.Team()
        t.name = "Minnesota"
        t.mascot = "Gopher"
        t.colors = ["maroon", "gold"]
        t.put()

        p = main.Player()
        p.name = "Doug Woog"
        p.position = "Center"
        p.team = t.key
        p.put()

        print main.get_player_or_404(p.key.id())
        print json.dumps(main.team_to_dict(main.Team(name="Minnesota", mascot="Gopher", colors=["maroon", "gold"])))
        print json.dumps(main.player_to_dict(main.Player(name="Kyle Rau", position="Forward", team=t.key)))