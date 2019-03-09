# LSGI

LSGI (Lambda Serverless Gateway Interface) is a simple WSGI adapter for AWS Lambda.
The main goal is to provide a simple way to get your WSGI apps running under Lambda using the AWS SAM toolchain.

## Installation

For now you can install this directly from the repo:
```bash
pip install git+https://github.com/mathom/lsgi.git
```

## Usage

Import LSGI in your app (in the example this is named `app.py`) and add a handler for Lambda:

```python
import lsgi
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

def lambda_handler(event, context):
    return lsgi.handler(app, event, context)
```

To deploy this with [AWS SAM](https://github.com/awslabs/serverless-application-model), try this template:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: 'AWS::Serverless-2016-10-31'

Resources:
  TestFlask:
    Type: 'AWS::Serverless::Function'
    Properties:
      Handler: app.lambda_handler
      Runtime: python3.6
      CodeUri: .
      Events:
        Root:
          Type: Api
          Properties:
            Path: /
            Method: ANY
Outputs:
  ApiEndpoint:
    Description: HTTP API endpoint
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

## Related projects
 * [Zappa](https://www.zappa.io/)
 * [aws-wsgi](https://github.com/slank/awsgi)
 * [aws-lambda-wsgi](https://github.com/truckpad/aws-lambda-wsgi)
