from distutils.core import setup
setup(
  name = 's3-tinify',
  packages = ['s3-tinify', 'boto3', 'tinify'], # this must be the same as the name above
  version = '0.1',
  description = 'Compress and overwrite images in your S3 bucket using the TinyPNG API.',
  author = 'Jun Tan',
  url = 'https://github.com/sc1f/s3-tinify', # use the URL to the github repo
  download_url = 'https://github.com/sc1f/s3-tinify/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['image', 'compression', 'AWS', 'S3', 'Tinify', 'TinyPNG', 'TinyJPG'], # arbitrary keywords
  classifiers = [],
)
