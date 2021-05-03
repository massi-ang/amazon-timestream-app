import * as cdk from '@aws-cdk/core'
import * as lambda from '@aws-cdk/aws-lambda'
import * as iam from '@aws-cdk/aws-iam'
import * as iot from '@aws-cdk/aws-iot'
import * as api from '@aws-cdk/aws-apigatewayv2'

let env = {
  "DB_NAME": "ruuvi",
  "TABLE_NAME": "sensors",
  "AWS_DATA_PATH": "$AWS_DATA_PATH:./models",
}

export class CdkStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    let role = new iam.Role(this, 'lambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      ]
    })

    role.attachInlinePolicy(new iam.Policy(this, 'timestreamWrite', {
      statements: [
        new iam.PolicyStatement({
          actions: [
            "timestream:*",
            "kms:DescribeKey",
            "kms:CreateGrant",
            "kms:Decrypt"
          ],
          resources: ["*"],
          effect: iam.Effect.ALLOW
        })
      ]
    }))



    let f = new lambda.Function(this, 'timestreamIngest', {
      code: new lambda.AssetCode('./src/timestreamIngest'),
      runtime: lambda.Runtime.PYTHON_3_8,
      memorySize: 128,
      handler: 'lambda.handler',
      role: role,
      environment: env
    })
    
    let rule = new iot.CfnTopicRule(this, 'ruuviToTimestream', {
      topicRulePayload: {
        sql: "SELECT topic(2) as location, 'home' as site, * from 'ruuvi/+'",
        awsIotSqlVersion: '2016-03-23',
        ruleDisabled: false,
        description: 'Enriches and send the Ruuvi tag messages to a Lambda function to TimeStream',
        actions: [
          {
            lambda: {
              functionArn: f.functionArn
            }
          }
        ],
      }
    })

    f.addPermission('iot-rule', {
      principal: new iam.ServicePrincipal('iot.amazonaws.com'),
      action: 'lambda:InvokeFunction'
    })

    let queryFun = new lambda.Function(this, 'queryFunc', {
      code: new lambda.AssetCode('./src/queryService'),
      handler: 'lambda.handler',
      memorySize: 256,
      runtime: lambda.Runtime.PYTHON_3_8,
      timeout: cdk.Duration.seconds(300),
      environment: env,
      role: role
    })

    let queryApi = new api.CfnApi(this, 'timestreamRuuviQueryApi', {
      protocolType: 'HTTP',
      name: 'timestreamRuuviQueryApi',
      target: queryFun.functionArn,
    })

    queryApi.corsConfiguration = {
      allowOrigins: ['*'],
      allowMethods: ['*']
    }

    
    new cdk.CfnOutput(this, 'apiUrl', {
      description: 'the query api',
      value: `https://${queryApi.ref}.execute-api.${this.region}.amazonaws.com`,
    })

    queryFun.addPermission('apiV2', {
      principal: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      action: 'lambda:InvokeFunction'
    })
  }
}
