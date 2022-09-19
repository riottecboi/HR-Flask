import boto3

s3 = boto3.client('s3',
                      aws_access_key_id='AKIA3CPS2UMCU3OJW3L7',
                      aws_secret_access_key='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'
                      )

# # Let's use Amazon S3
# s3 = boto3.resource("s3",
#                       aws_access_key_id='AKIA3CPS2UMCU3OJW3L7',
#                       aws_secret_access_key='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')

# Print out bucket names
# s3.download_file(
#     Bucket="hr-fiver-test", Key="test.png", Filename="test.png"
# )

s3.upload_file(
    Filename="requirements.txt",
    Bucket="hr-fiver-test",
    Key="requirement.txt",
)