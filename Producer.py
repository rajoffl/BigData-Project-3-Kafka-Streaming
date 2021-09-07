#!/usr/bin/env python
from kafka import KafkaClient, SimpleProducer
import json,requests

# Creating Kafka client
kafka = KafkaClient('localhost:9092')

#Creating a Kafka producer instance
meetup_producer = SimpleProducer(kafka)

r = requests.get("https://stream.meetup.com/2/rsvps",stream=True)

# Sending messages to Consumer.
for line in r.iter_lines():
	meetup_producer.send_messages('meetup',line)
	obj = json.loads(line.decode('utf-8'))
        rsvps= (obj['group']['group_city'])
	print (rsvps)

kafka.close()