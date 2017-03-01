#!/usr/bin/env python3

import boto3, tinify, os, sys, time
import multiprocessing
from multiprocessing import Process, Queue

try:
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, "creds.py")
    print("Looking for credential file:", str(config_file))
    open(config_file)
    print("Credential file found!")
    import creds
    AWS_ACCESS_KEY_ID = creds.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = creds.AWS_SECRET_ACCESS_KEY
    TINIFY_KEY = creds.TINIFY_KEY
    AWS_BUCKET = creds.AWS_BUCKET

except:
    print("No credential file, prompting manual credential entry...")
    AWS_ACCESS_KEY_ID = raw_input("Enter your AWS access key ID: ")
    AWS_SECRET_ACCESS_KEY = raw_input("Enter your AWS secret access key: ")
    TINIFY_KEY = raw_input("Enter your Tinify API key: ")
    AWS_BUCKET = raw_input("Enter the name of the AWS bucket you want to access: ")
    RESIZE_WIDTH = int(input("Enter the width you want to resize your images to (leave blank to keep original size): "))
    creds = [AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, TINIFY_KEY, AWS_BUCKET, RESIZE_WIDTH]
    new_cred_file = os.path.join(os.path.dirname(__file__), "creds.py")

    with open(new_cred_file, "w") as output_creds:
        rw = "RESIZE_WIDTH = %d" % RESIZE_WIDTH
        output_creds.write("AWS_ACCESS_KEY_ID = " + str(AWS_ACCESS_KEY_ID) + "\n")
        output_creds.write("AWS_SECRET_ACCESS_KEY = " + str(AWS_SECRET_ACCESS_KEY) + "\n")
        output_creds.write("TINIFY_KEY = " + str(TINIFY_KEY) + "\n")
        output_creds.write("AWS_BUCKET = " + str(AWS_BUCKET) + "\n")
        output_creds.write(rw)
        print("New creds.py written!")

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

def compress_save_image(image):
    print("Processing", image)
    start = time.time()
    img_name = str(image)
    temp_name = os.path.basename(img_name)
    temp_save_location = os.path.join("_temp", temp_name)
        # saving
    orig = tinify.from_url("https://" + str(AWS_BUCKET) + ".s3.amazonaws.com/" + image)
    if RESIZE_WIDTH != None:
        resized = orig.resize(
            mode="scale", 
            width=RESIZE_WIDTH
        )
        final = resized.to_file(temp_save_location)
    else:
        final = orig.to_file(temp_save_location)
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
    end = time.time() - start
    print("This took", end, "seconds")


def read_image_queue(queue):
    while True:
        img = queue.get()
        compress_save_image(img)
        if img == "BREAK":
            break

def write_image_queue(image, queue):
    queue.put(source_list[image])
    if image == "BREAK":
        queue.put("BREAK")


if __name__ == '__main__':
    # TODO build queue/process workers
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
    if len(jobs) == 0:
        os.rmdir("_temp")