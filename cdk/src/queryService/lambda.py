import boto3
import json

tsq = boto3.client('timestream-query', region_name='us-east-1')

QUERY_SIMPLE ="""select bin(time, {bin}) as binned_time, avg(case when measure_name='{measure}' then measure_value::double else null end) as avg_temp
from ruuvi.sensors
where time > ago({time}) and location = '{location}'
group by bin(time, {bin})
order by bin(time, {bin})"""

QUERY_MULTI = """select bin(time, {bin}) as binned_time, avg(case when measure_name='temperature' then measure_value::double else null end) as avg_temp,
avg(case when measure_name='humidity' then measure_value::double else null end) as avg_humidity,
avg(case when measure_name='pressure' then measure_value::double else null end) as avg_pressure
from ruuvi.sensors
where time > ago({time}) and location = '{location}'
group by bin(time, {bin})
order by bin(time, {bin})"""

multipliers = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 3660*24
}

def bin_from_time(t, points):
    n = t[:-1]
    u = t[-1]
    m = multipliers[u]
    seconds = (int(n) * m) / points
    if seconds == 0:
        seconds = 1
    return f'{seconds}s'

def handler(event, context):
    print(event)
    if not event['rawPath'] in ['/simple', '/multi', '/query']:
        return {
            "statusCode": 403
        }
    if not event['rawPath'] == '/query' and (not 'queryStringParameters' in event or not 'time' in event['queryStringParameters'] \
            or not 'location' in event['queryStringParameters']):
            return {
                "statusCode": 400,
                "body": "Invalid query - query paramters missing"
            }
    if event['rawPath'] == '/query':
        query = json.loads(event['body'])['code']
        try:
            paginator = tsq.get_paginator('query')
            res = paginator.paginate(QueryString=query)
            data = None
            for page in res:
                print(page)
                if data is None:
                    page.pop('ResponseMetadata')
                    data = page
                else: 
                    data['Rows'] = data['Rows'] + page['Rows']
            return {
                "statusCode": 200,
                "body": json.dumps(data),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        except Exception as ex:
            print(ex)
            return {
                "statusCode": 400,
                "body": json.dumps({'error': str(ex)}),
                "headers": {
                    "Content-Type": "application/json"
                }
            }
    if event['rawPath'] == '/simple': 
        if  not 'measure' in event['queryStringParameters']:       
            return {
                "statusCode": 400,
                "body": "Invalid query - query paramters missing"
            }
        time = event['queryStringParameters']['time']
        measure = event['queryStringParameters']['measure']
        location = event['queryStringParameters']['location']
        points = int(event['queryStringParameters'].get('points', 50))
        query = QUERY_SIMPLE.format(time=time, location=location, measure=measure, bin=bin_from_time(time, points))
        print(query)
        res = tsq.query(QueryString=query)
        data = [{'time':r['Data'][0]['ScalarValue'].split('.')[0].replace(' ', 'T'), 'value':float(r['Data'][1]['ScalarValue'])} for r in res['Rows']]
        return {
            "statusCode": 200,
            "body": json.dumps(data),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    if event['rawPath'] == '/multi': 
        time = event['queryStringParameters']['time']
        location = event['queryStringParameters']['location']
        points = int(event['queryStringParameters'].get('points', 50))
        query = QUERY_MULTI.format(time=time, location=location, bin=bin_from_time(time, points))
        print(query)
        res = tsq.query(QueryString=query)
        data = [{'time': r['Data'][0]['ScalarValue'].split('.')[0].replace(' ', 'T'), 'temperature':float(r['Data'][1]['ScalarValue']), 'humidity':float(
            r['Data'][2]['ScalarValue']), 'pressure':float(r['Data'][3]['ScalarValue'])} for r in res['Rows']]
        return {
            "statusCode": 200,
            "body": json.dumps(data),
            "headers": {
                "Content-Type": "application/json"
            }
        }
