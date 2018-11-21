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
from google.appengine.api.images import Image as x
from PIL import Image
import StringIO




# gsutil -d ls | grep -i bear
ACCESS_TOKEN = 'ya29.GqMBWwZ1DW-0qEO9Eh4U_wnhTNVufywTwRGokDs1ng7wKDwTsZPsAAEOVgDBj07SYyR5c73vP8QJCkIE-J0CmtIWZE8cNq7qIKdpoRwuURd1wMcZESivSNbIeiQdCQx3u_N35z5yPHl8RI6HN-6admo-bgMQk9qrlvujL10ihEkgJnfntxcVF2mF5pSotGFh9sJJ5hHI0rQ8Roo-_eH1wO4gHMvHTw'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def merge_images(buffers):
	counter = 0
	page_num = 1
	cont = True
	X = 660
	Y = 960
	while cont:
		new_im = Image.new('RGB', (X, Y))
		for i in xrange(0,X,X/3):
			for j in xrange(0,Y,Y/3):
				if counter < len(buffers):
					im = Image.open(StringIO.StringIO(buffers[counter]))
					#im = Image.frombytes('RGB', (640, 480), buffers[counter], 'raw')
#Image.open(buffers[counter])
					im.thumbnail((800,800))
					new_im.paste(im, (i,j))
					counter += 1
				else:
					cont = False
		page_num += 1
	return new_im


class MainPage(webapp2.RequestHandler):
    def get(self):
    	template = JINJA_ENVIRONMENT.get_template('a.html')
        self.response.write(template.render({}))

class DeckCreator(webapp2.RequestHandler):
	def post(self):
		bucket_name = bucket_name = os.environ.get('BUCKET_NAME',
                               app_identity.get_default_gcs_bucket_name())
   		gcs.common.set_access_token(ACCESS_TOKEN)
		content = self.request.get('deck')
		lines = content.splitlines()
		buffers = []
		with open('CardMap.json', 'r') as input_json_handle:
			card_map = json.load(input_json_handle)
			multiverse_id = ''
			for line in lines:
				tokens = line.split(' ')
				quantity = tokens[0]
				if is_number(tokens[-1]):
					name = ' '.join(tokens[1:-2])
					set = tokens[-2]
					num = tokens[-1]
				else:
					name = ' '.join(tokens[1:])
				list_of_multiverse_ids = card_map[name.upper()]
				multiverse_id = max(list_of_multiverse_ids)
				gcs_file = gcs.open('/{}/images/{}.png'.format(bucket_name, multiverse_id))
				contents = gcs_file.read()
				#tempBuff = StringIO.StringIO()
				#tempBuff.write(contents)
				#tempBuff.seek(0)
				buffers.append(contents)
				gcs_file.close()
		
		self.response.headers['Content-Type'] ='image/png'
		#self.response.headers['Content-Type'] ='text/html'
		#print merge_images(buffers).tobytes()
		new_image = merge_images(buffers)
		img_io = StringIO.StringIO()
		new_image.save(img_io, 'PNG')
		img_io.seek(0)
		self.response.write(img_io.getvalue())

	def get(self):
		self.response.write('You should not have gotten here')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/create', DeckCreator)
], debug=True)
