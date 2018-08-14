# s3-tinify
*Compress images in an S3 bucket using the TinyPNG API, and rewrite images with compressed versions*

This is a modified version of [s3-tinify][https://github.com/sc1f/s3-tinify].
It doesn't do any resizing, but only focuses on compressing/optimizing PNG and JPEG files. 
To use this, we have to make sure that the bucket has the permissions: GetObjectTagging and PutObjectTagging. 

It overwrites the existing versions. 

LIMITS: TinyPNG API supports up to 500 conversions per month. A paid plan can be used after that number. 

Using the [Tinify](https://github.com/tinify/tinify-python) API from TinyPNG, we can achieve huge space reductions (8MB image => 24kb after resizing from 36 megapixels > 400px for thumbnail) in order to serve images for production usage. This package provides a wrapper around the Tinify API, and uses it to automatically compress images stored in your S3 bucket. The package then overwrites those images, assuming that you only require the uncompressed versions.

## Usage

`python2 compress-s3-tinypng.py` 


## Setup

1. Installation: `git clone https://github.com/rootstrap/compress-s3-tinypng` 

2. Dependencies: `pip install -r requirements.txt` 

	- [Boto3](https://github.com/boto/boto3), [Tinify](https://github.com/tinify/tinify-python)

3. Load credentials:

	- On wherever you cloned the repo, create a file named `creds.py`. 

	- Inside `creds.py`, copy these lines and replace the sample variables with your own access keys and parameters:
	```
	AWS_ACCESS_KEY_ID = 'YOUR_AWS_ID_HERE'
	AWS_SECRET_ACCESS_KEY = 'YOUR_AWS_SECRET_HERE'
	TINIFY_KEY = "YOUR_TINIFY_API_KEY_HERE"
	AWS_BUCKET = "YOUR_BUCKET_NAME"
	```

	- `creds.py` is ignored by Git.

	- On AWS, make sure the user you provide credentials for has full read/write access to the bucket.

	- Boto3 (the AWS python SDK) will [look for credentials](http://boto3.readthedocs.io/en/latest/guide/configuration.html) on its own, but creds.py provides a layer of redundancy. If you don't have a creds.py, the script will prompt you for input and create one for you. 

	- The Tinify API has a free tier of 500 images a month. If you go past that, Tinify will throw an error and it will halt the program.


## License

MIT

## Credits
rs-s3-Tinypng is maintained by [Rootstrap](http://www.rootstrap.com) 
[<img src="https://s3-us-west-1.amazonaws.com/rootstrap.com/img/rs.png" width="100"/>](http://www.rootstrap.com)