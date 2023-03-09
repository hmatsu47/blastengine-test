# blastengine-test

blastengine テスト用リポジトリ

## AWS Lambda 関数

※あらかじめ - [blastengine Python SDK](https://pypi.org/project/blastengine/) を Lambda Layer 化しておき、Lambda 関数で使用する

- [blastMailSender](lambda/blastMailSender/README.md)
  - DynamoDB table (for mail sender) にメールの情報を登録するとメールを送信
    - id : Partition key
    - fromAddress : Sender address
    - fromName : Sender name
    - to : Receiver address
    - subject : Subject (Title)
    - textPart : Content body (Text only)
- [blastBounceReceiver](lambda/blastBounceReceiver/README.md)
  - Bounce を Webhook から受信して DynamoDB table (for bounce) に書き込み
  - 準備中
