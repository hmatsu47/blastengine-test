## 必要な準備

### blastengine

- API Key

### AWS

- Route 53 Public Hosted Zone
  - SPF record
    - https://qiita.com/goofmint/items/ccfb316d4fc2e5c4d412#%E9%80%81%E4%BF%A1%E5%85%83%E3%83%89%E3%83%A1%E3%82%A4%E3%83%B3%E3%81%AEspf%E3%82%92%E8%A8%AD%E5%AE%9A%E3%81%99%E3%82%8B
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
      - `dynamodb:DeleteItem`
        - Resource : `arn:aws:dynamodb:[Region]:[Account ID]:table/[for mail sender]`
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
      - `TABLE_SENDER` : Table name (for sender)
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

### blastengine

- DKIM
