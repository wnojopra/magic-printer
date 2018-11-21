import json
import requests
from google.cloud import storage
storage_client = storage.Client()

bucket_name = 'mtg-images'
bucket = storage_client.get_bucket(bucket_name)

base_url = 'http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid={}&type=card'
m_id = 1
c_name = ''
write_flag = False
try:
  with open('CardMap.json', 'r') as json_file_handle:
    card_to_ids = json.load(json_file_handle)
    for card_name, multiverse_id_list in card_to_ids.iteritems():
      card_name = card_name.encode('utf-8')
      c_name = card_name
      for multiverse_id in multiverse_id_list:
        if multiverse_id == 409897:
          write_flag = False
        m_id = multiverse_id
        image_url = base_url.format(multiverse_id)
        if write_flag:
          r = requests.get(image_url)
          destination_blob_name = 'images/{}.png'.format(multiverse_id)
          blob = bucket.blob(destination_blob_name)
          blob.upload_from_string(r.content)
        print('uploaded {} as {}'.format(card_name, multiverse_id))
        #with open('{}.png'.format(multiverse_id), 'wb') as outfile:
          #outfile.write(r.content)
except Exception as e:
  print('last known card, m_id was {}, {}'.format(c_name, m_id))
  raise
