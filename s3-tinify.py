#!/usr/bin/env python3

import boto3, tinify, os, sys
import creds

# check for ~/.aws/config
#print("Attempting to find ~/.aws/credentials")

try:
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, "creds.py")
    print("Looking for credential file:", str(config_file))
    open(config_file)
    print("Credential file found!")
    AWS_ACCESS_KEY_ID = creds.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = creds.AWS_SECRET_ACCESS_KEY
    TINIFY_KEY = creds.TINIFY_KEY
    AWS_BUCKET = creds.AWS_BUCKET
    AWS_REGION = creds.AWS_REGION

except:
    print("No credential file, prompting manual credential entry...")
    AWS_ACCESS_KEY_ID = input("Enter your AWS access key ID: ")
    AWS_SECRET_ACCESS_KEY = input("Enter your AWS secret access key: ")
    TINIFY_KEY = input("Enter your Tinify API key: ")
    AWS_BUCKET = input("Enter the name of the AWS bucket you want to access: ")
    AWS_REGION = input("Enter the region of your AWS bucket: ")

# TINIFY CONFIG
tinify.key = TINIFY_KEY

#construct bucket url
#S3_URL = 'https://%s.s3.amazonaws.com' % AWS_BUCKET

s3 = boto3.client(
    's3', 
    aws_access_key_id=AWS_ACCESS_KEY_ID, 
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# get all objects in bucket, and push only images to a sourcelist
source_list = []

for key in s3.list_objects_v2(Bucket=AWS_BUCKET)['Contents']:
        filename = key['Key']
        tag = s3.get_object_tagging(
            Bucket = AWS_BUCKET,
            Key = key['Key']
            )
        if ".jpg" in filename or ".jpeg" in filename or ".png" in filename:
            if len(tag['TagSet']) != 0:
                is_compressed = tag['TagSet'][0]["Key"] == "s3-tinify-compressed" and tag['TagSet'][0]["Value"] == "True" # TODO handle multiple values
            else:
                is_compressed = False

            if is_compressed:
                continue
            else:
                source_list.append(filename)
                # print(filename)

if len(source_list) == 0:
    print("No images to compress!")
    sys.exit()
else:
    print("Found " + str(len(source_list)) + " images to process.")
    # create temp directory
    #temp_dir = os.makedirs(_("temp"))

#start image processing
success_count = 0

def store_image(img, img_name, bucket, region):
    try:
        img.store(
            service = "s3",
            aws_access_key_id = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            region = region,
            path = bucket + img_name
        )
        print(img_name, "has been saved to your S3 bucket!")
    except:
        print(img_name, "could not be saved to S3!")


def write_metadata(img_key, bucket):
    s3.put_object_tagging(
        Bucket = bucket,
        Key = img_key,
        Tagging = {
            "TagSet" : [
                {
                    "Key": "s3-tinify-compressed",
                    "Value": "True"
                }
            ]
        }
    )
    print(img_key, "has been marked as compressed!")

for image in source_list:
    try:
        print("Processing", image)
        orig = tinify.from_url("https://" + str(AWS_BUCKET) + ".s3.amazonaws.com/" + image) # TODO .resize()
        print(image, "has been successfully compressed.")
        store_image(orig, image, AWS_BUCKET, AWS_REGION)
        #write_metadata(img, AWS_BUCKET)
        success_count += 1
    except:
        print("***", image, "could not be processed! ***")
        pass

print(success_count, "images have been processed and saved to S3.")
sys.exit()