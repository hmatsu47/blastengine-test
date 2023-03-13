## 必要な準備

### AWS

- KMS customer key
  - for DynamoDB tables
    - Create
- DynamoDB tables
  - for bounce
    - Partition key : deliveryId (Number)
- Lambda Function
  - IAM Role
    - Create new Role
      - Default Basic role (for CloudWatch logs)
    - Add Policy
      - `dynamodb:GetItem`
        - Resource : `arn:aws:dynamodb:[Region]:[Account ID]:table/[for mail sent log]`
      - `dynamodb:PutItem`
        - Resource : `arn:aws:dynamodb:[Region]:[Account ID]:table/[for bounce]`
  - Configuration
    - General
      - Timedout : 30 sec.
    - Environment variables
      - `TABLE_BOUNCE` : Table name (for bounce)
      - `TABLE_SENT_LOG` : Table name (for sent log)
- API Gateway
  - Resource Path
    - Long and random path
      - Action : POST only
        - Integration request : type LAMBDA_PROXY
      - POST Method Response : add 500
        - `application/json`
        - Empty
  - Stage
    - `v1`
- KMS customer key
  - for DynamoDB tables
    - Add Role (for Lambda)

### blastengine

- Settings
  - Webhook
    - Status : Enable
    - Endpoint URL : API Gateway URL
    - Events
      - Drop
      - Hard Error
