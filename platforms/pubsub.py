
import os
from google.cloud import pubsub_v1


os.environ['GOOGLE_APPLICATION_CREDENTIALS']='slackreport-pubsub.json'


publisher= pubsub_v1.PublisherClient()
topic_path='projects/workflow-394611/topics/slack-report'

data = 'message'
data = data.encode('utf-8')
attributes = {
    'channel_id':"XXXXXXX",
    'response_url':"YYYYYYYY"
}

future = publisher.publish(topic_path,data, **attributes)
print(f'published message id {future.result()}')

