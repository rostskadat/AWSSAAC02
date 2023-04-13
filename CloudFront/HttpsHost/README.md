# CloudFront / HttpsHost

*NOTE* THE STACK MUST BE CREATED IN US-EAST-1

Showcase the handling of the Host header in an HTTPS Context

## Building

```shell
sam build 
sam deploy --no-fail-on-empty-changeset --no-confirm-changeset --tags "PLATFORM=SAPC01" 
``` 

## Testing

With SAM you can test your function locally:

```shell
sam local invoke --event events/events.json HttpsHostFunction
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```shell
aws cloudformation delete-stack --stack-name SAPC01-HttpsHost
```

## Details

*Author*: rostskadat