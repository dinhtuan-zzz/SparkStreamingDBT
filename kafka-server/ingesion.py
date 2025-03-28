import requests
import pandas as pd
import boto3
from datetime import datetime
from kafka import KafkaProducer

def readApi():
    getResponse = requests.get('https://random-data-api.com/api/v3/projects/4e5784b9-cd02-449b-b83e-27da0458e2e6?api_key=ezQpe6GRftvLFRailG2WEQ')
    data = getResponse.json()
    df = pd.DataFrame(data)

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers=['kafka-server:9092'],
    value_serializer=json_serializer
)

def writeToKafka(new_df):
    producer.send('daily', value = new_df)
    producer.flush()

if __name__ == '__main__':
    for i in range(1000):
        writeToKafka(readApi())

