import boto3
import os
from time import time
import botocore

config = botocore.client.Config(endpoint_discovery_enabled=True)
tsc = boto3.client('timestream-write', region_name='us-east-1', config=config)
DB_NAME = os.environ.get('DB_NAME')
TABLE_NAME = os.environ.get('TABLE_NAME')

def ruuvi_data_to_records(data):
    records = []
    for k, v in data.items():
        if k in ['temperature', 'humidity', 'pressure', 'battery', 'txPower']:
            records.append({
                'MeasureName': k,
                'MeasureValue': str(v)
            })
    return records

def handler(event, context):
    dimensions = [
        {'Name': 'location', 'Value': event['location']},
        {'Name': 'site', 'Value': event['site']}
    ]
    tsc.write_records(DatabaseName=DB_NAME,
                      TableName=TABLE_NAME,
                      CommonAttributes={
                          'Dimensions': dimensions,
                          'MeasureValueType': 'DOUBLE',
                          'Time': str(int(time() * 1000)),
                          'TimeUnit': 'MILLISECONDS'
                      },
                      Records=ruuvi_data_to_records(event))
