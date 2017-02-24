#!/usr/bin/env python3

import boto3, tinify, os, sys
import multiprocessing
import creds

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

s3 = boto3.client(
    's3', 
    aws_access_key_id=AWS_ACCESS_KEY_ID, 
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# get all objects in bucket, and push only images to a sourcelist
source_list = []

def get_s3_objects():
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

def make_temp_directory():
    if len(source_list) == 0:
        print("No images to compress!")
        sys.exit()
    else:
        print("Found " + str(len(source_list)) + " images to process.")
        # create temp directory
        if not os.path.exists("_temp"):
            temp_dir = os.makedirs(("_temp"))

#start image processing
success_count = 0

def compress_save_image(image):
    print("Processing", image)
    img_name = str(image)
    temp_name = os.path.basename(img_name)
    temp_save_location = os.path.join("_temp", temp_name)
        # saving
    orig = tinify.from_url("https://" + str(AWS_BUCKET) + ".s3.amazonaws.com/" + image)
    resized = orig.resize(
        mode="scale", 
        width=500
    )
    final = resized.to_file(temp_save_location)
    # TODO refactor and remove redundant try/catch blocks
    if ".jpg" in temp_name or ".jpeg" in temp_name:
        content_type = "image/jpeg"
    elif ".png" in temp_name:
        content_type = "image/png"

    with open(temp_save_location, 'rb') as source:
        img_data = source.read()

    print(image, "has been successfully compressed.")
    # upload to S3, overwrite old file
    save_img = s3.put_object(
        Body = img_data,
        Bucket = AWS_BUCKET,
        Key = image,
        ContentType = content_type
    )

    print(img_name, "has been saved to S3 bucket", AWS_BUCKET)
    s3.put_object_tagging(
        Bucket = AWS_BUCKET,
        Key = image,
        Tagging = {
            "TagSet" : [
                {
                    "Key": "s3-tinify-compressed",
                    "Value": "True"
                }
            ]
        }
    )
    print(image, "has been marked as compressed!")
    success_count += 1
    os.rmdir("_temp")


if __name__ == '__main__':
    get_s3_objects()
    make_temp_directory()
    jobs = []
    for i in range(len(source_list)):
        proc = multiprocessing.Process(
            target = compress_save_image, 
            args = (source_list[i],)
        )
        jobs.append(proc)
        proc.start()