# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

import webapp2
import jinja2
import cloudstorage as gcs
from google.appengine.api import app_identity

ACCESS_TOKEN = 'ya29.GqMBWwZMbfg_ugmpfXAYHfbWnTN0xU3cnLseK_AgxHH2mhAXZ2hkydMnm09LBc9CBCIsNCbxZ-tRkGRLHDOc3xCTmx_TZWYKCMG52dJ-cI4XD1TCBRVj3ETI4G5QME0UhRIjZej-hl2w2NoQKR8s59vfYh8xPMAYfTPev_poioWgJfeCkkVt_3KcNIfDs9rnoJFEQr9cnAIUEb0PizSlqy-rf2cBmA'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
    	template = JINJA_ENVIRONMENT.get_template('a.html')
        self.response.write(template.render({}))

class DeckCreator(webapp2.RequestHandler):
	def post(self):
		bucket_name = 'mtg-images'
		content = self.request.get('deck')
		multiverse_id = ''
		with open('CardMap.json', 'r') as input_json_handle:
			card_map = json.load(input_json_handle)
			list_of_multiverse_ids = card_map[content.upper()]
			multiverse_id = max(list_of_multiverse_ids)
		gcs.common.set_access_token(ACCESS_TOKEN)
		gcs_file = gcs.open('/{}/images/{}.png'.format(bucket_name, multiverse_id))
		contents = gcs_file.read()
		gcs_file.close()
		self.response.headers['Content-Type'] ='image/png'
		self.response.write(contents)
	
	def get(self):
		self.response.write('You should not have gotten here')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', DeckCreator)
], debug=True)
