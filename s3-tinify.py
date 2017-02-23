#!/usr/bin/env python3

import boto3, tinify, os
from os.path import expanduser

# check for ~/.aws/config
print("Attempting to find ~/.aws/credentials")

'''
try:
    user_path = os.path.expanduser("~")
    config_file = os.path.join(user_path, ".aws/credentials")
    open(config_file)
    print("AWS configuration file found!")
except:
    print("No AWS configuration file, prompting manual credential entry...")
    AWS_ACCESS_KEY_ID = input("Enter your AWS access key ID: ")
    AWS_SECRET_ACCESS_KEY = input("Enter your AWS secret access key: ")
'''


#TINIFY_KEY = input("Enter your tinify API key: ")
AWS_BUCKET = input("Enter the bucket name you want to download from & save to: ")
DIRECTORY = input("Enter the directory you want to act on inside the bucket: ")
#tinify.key = TINIFY_KEY

#construct bucket url
#S3_URL = 'https://%s.s3.amazonaws.com' % AWS_BUCKET

# begin interface with s3
s3 = boto3.client('s3')
# get bucket
for key in s3.list_objects(Bucket=AWS_BUCKET)['Contents']:
        print(key['Key'])

#tinify.from_url()

#save to s3
'''
IMAGE_VAR_HERE.store(
    service="s3",
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region="us-west-1",
    path="example-bucket/my-images/optimized.jpg"
)

# handle errors

for file in arguments.file:
    orig = tinify.from_file(file)
    if scale_size != None:
        resized = orig.resize(
                method="scale",
                width = scale_size
                )
        resized.to_file(save_dir + file)
        print(file + " has been compressed.")
    else:
        orig.to_file(save_dir + file)
        print(file + " has been compressed.")
'''

