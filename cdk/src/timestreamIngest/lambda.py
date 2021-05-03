import boto3
import os
from time import time
import botocore

REGION_NAME = os.environ.get('TIMESTREAM_REGION')
DB_NAME = os.environ.get('DB_NAME')
TABLE_NAME = os.environ.get('TABLE_NAME')
TIME_FIELD = 'time'

tsc = boto3.client('timestream-write', region_name=REGION_NAME)

def data_to_records(data):
    records = []
    for k, v in data.items():
        try:
            x = float(v)
            if k[0:2] != 'd_' and k != TIME_FIELD:
                records.append({
                    'MeasureName': k,
                    'MeasureValue': str(x)
                })
        except: 
            pass
    return records

def handler(event, context):
    dimensions = [{'Name': x[2:], 'Value': event[x]} for x in event.keys() if x[0:2] == 'd_']
    if TIME_FIELD in event:
        t = event[TIME_FIELD]
    else:
        t = str(int(time() * 1000))

    tsc.write_records(DatabaseName=DB_NAME,
                      TableName=TABLE_NAME,
                      CommonAttributes={
                          'Dimensions': dimensions,
                          'MeasureValueType': 'DOUBLE',
                          'Time': t,
                          'TimeUnit': 'MILLISECONDS'
                      },
                      Records=data_to_records(event))
