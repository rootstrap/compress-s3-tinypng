# s3-tinify
*Compress images in an S3 bucket using the TinyPNG API, and rewrite images with compressed versions

Using the [Tinify](https://github.com/tinify/tinify-python) API from TinyPNG, we can achieve huge space reductions (8MB image => 24kb after resizing from 36 megapixels > 400px for thumbnail) in order to serve images for production usage. This package provides a wrapper around the Tinify API, and uses it to automatically compress images stored in your S3 bucket. The package then overwrites those images, assuming that you only require the uncompressed versions.

## Usage

`python3 s3-tinify.py` or `s3-tinify` (if moved into $PATH)


## Setup

1. Installation: `git clone https://github.com/sc1f/s3-tinify` or (PENDING) `pip install s3-tinify`

2. Dependencies: `pip install -r requirements.txt` or (PENDING) pip will handle dependencies.

	- [Boto3](https://github.com/boto/boto3), [Tinify](https://github.com/tinify/tinify-python)

3. Load credentials:

	- On wherever you cloned the repo, create a file named `Creds.py`. If you want to run this from $PATH, Creds.py must be in your $PATH too. This is a temporary workaround until I figure out a better way to access AWS variables.

	- Inside `Creds.py`, copy these lines and replace the sample variables with your own access keys and parameters:
	```
	AWS_ACCESS_KEY_ID = 'YOUR_AWS_ID_HERE'
	AWS_SECRET_ACCESS_KEY = 'YOUR_AWS_SECRET_HERE'
	TINIFY_KEY = "YOUR_TINIFY_API_KEY_HERE"
	AWS_BUCKET = "YOUR_BUCKET_NAME"
	```

	- `Creds.py` is ignored by Git.

	- On AWS, make sure the user you provide credentials for has full read/write access to the bucket.

	- Boto3 (the AWS python SDK) will [look for credentials](http://boto3.readthedocs.io/en/latest/guide/configuration.html) on its own, but Creds.py provides a layer of redundancy (WHICH I MAY FIX LATER DEPENDING ON NEED.) The Tinify API requires a key to be passed on it regardless, and hardcoding it is not a good idea.

	- The Tinify API has a free tier of 500 images a month. If you go past that, Tinify will throw an error and it will halt the program.


## Why?

While working on the [Daily Texan Student Government Explorer](https://github.com/sc1f/dtsg), I didn't expect there to be uploads of huge images that were more than a few megabytes large. I woke up one morning to texts saying that our server kept throwing 502 errors while trying to add candidates through our survey. 

I spent the morning before class sitting in bed and writing up an emergency fix, including migrating our Gunicorn workers to Tornado, and doubling the number of worker daemons on the server. I then got to work migrating our production project to AWS S3, which wouldn't have this chokehold. 

I wanted, however, to make the experience seamless, and not have to change any URLs in our DB once the user has uploaded their image. I also wanted to have the compression/resizing on-the-fly abilities that [django-imagekit](http://django-imagekit.readthedocs.io/en/latest/) provided with their `ProcessedImageField`. In order to satisfy all those requirements, S3 and Tinify fit the bill. 

## Contributing

**Developed by [Jun Tan](https://github.com/sc1f), from beginning to first production-ready version in one very long, very caffeinated day.**

All the code is in `s3-tinify.py`. Travis CI integration is on the way.

## License

MIT