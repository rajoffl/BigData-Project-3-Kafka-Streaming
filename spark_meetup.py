from __future__ import print_function

import json
import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

f_count = 0;

# Function to aggregate the city counts to the alreaddy existing value 
def city_count(newValue, oldValue):
    if oldValue is None:
        oldValue = 0

    return sum(newValue)+oldValue

if __name__ == "__main__":

    #Creaitng spark Context since we are submitting from the command line
    sc = SparkContext("local[2]",appName="MeetupStreaming")
    sc.setLogLevel("WARN")

    #Creating the streaming context
    ssc = StreamingContext(sc, 2)
    ssc.checkpoint("checkpoint")

    #Getting the zkQuorum port and topic value from command line
    zkQuorum, topic = sys.argv[1:]

    #Assigning the created stream to receive messages from kafka meetup
    sstream = KafkaUtils.createStream(ssc, zkQuorum, "1", {topic: 1})

    rsvps = sstream.map(lambda x: x[1])
    rsvps_json = rsvps.map(lambda x: json.loads(x.encode('ascii','ignore')))

    #Filtering only the messages belong to the U.S.
    us_only = rsvps_json.filter(lambda x: x['group']['group_country']=='us')

    #Extracting the city name from messages.
    city_pair = us_only.map(lambda x: (x['group']['group_city'],1))

    #Calling the function to get the city count
    city_count= city_pair.updateStateByKey(city_count)
                                
    #Storing the output files in a local file system to get the visualization done.
    city_count.saveAsTextFiles('file:/home/cloudera/streamData/output')
    #rs.pprint()
    ssc.start()
ssc.awaitTermination()