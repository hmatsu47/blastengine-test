## 必要な準備

### blastengine

- API Key
- DKIM

### AWS

- Route 53 Public Hosted Zone
  - SPF record
  - DKIM record
    - https://powerdmarc.com/ja/power-dmarc-toolbox/
      - Generator Tools -> DKIM Record Generator
- DynamoDB tables
  - for mail sender
    - Partition key : id (String)
  - for mail sent log
    - Partition key : deliveryId (Number)
- KMS customer key
  - for Lambda (Environment variables)
    - Create
- Lambda Function
  - IAM Role
    - Create new Role
      - Default Basic role (for CloudWatch logs)
    - Add Policy
      - `dynamodb:ListStreams`
        - Resource : `*`
      - `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Query`
        - Resource : `arn:aws:dynamodb:[Region]:[Account ID]:table/[for mail sent log]`
      - `dynamodb:GetShardIterator`, `dynamodb:DescribeStream`, `dynamodb:GetRecords`
        - Resource : `arn:aws:dynamodb:[Region]:[Account ID]:table/[for mail sent log]/stream/*`
  - Layer
    - [blastengine Python SDK](https://github.com/blastengineMania/blastengine-py)
  - Configuration
    - General
      - Timedout : 30 sec.
    - Environment variables
      - `BLASTENGINE_API_USER` : blastengine User Name
      - `BLASTENGINE_API_KEY` : blastengine API Key
      - `TABLE_SENT_LOG` : Table name (for sent log)
- KMS customer key
  - for DynamoDB tables
    - Add Role (for Lambda)
  - for Lambda (Environment variables)
    - Add Role (for Lambda)
- DynamoDB tables
  - for mail sender
    - DynamoDB Streams
      - Trigger : lambda function
        - Batch size : 100
