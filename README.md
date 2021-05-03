# Timestream Demo

## Backend

The backend consists of an IoT Rule and a lambda function to push the data to Timestream. 

We also deploy an HTTP API for querying the data.

> **NOTE**:  The API is currently publicly available. Consider adding Cognito and JWT for authentication.

To deploy the backend:

```bash
cd timestream/cdk
npm i
npm run build
cdk deploy
```

Note the HTTP API endpoint which is displayed in the output.

TODO: use configuration file to setup the endpoint for the client. 

## Frontend

The frontend is developed in Vuejs and uses the Echarts library for charting. 

To run the frontend locally:

```bash
cd timestream/timestream-explorer
npm i
npm run serve
```


## TODO
- AWS Amplify for authentication and hosting
- Additional visualization widgets based on ECharts components
- Additional queries
