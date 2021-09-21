import os
"""
AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME="nubebar"
AWS_S3_ENDPOINT_URL="https://sfo3.digitaloceanspaces.com"
#AWS_LOCATION=f"https://{AWS_STORAGE_BUCKET_NAME}.sfo3.digitaloceanspaces.com"
AWS_LOCATION="https://nubebar.sfo3.digitaloceanspaces.com"
AWS_S3_OBJECT_PARAMETERS = {
	"CacheControl": "max-age=86400",
}
DEFAULT_FILE_STORAGE="app.cdn.backends.MediaRootS3Boto3Storage"
STATICFILES_STORAGE="app.cdn.backends.StaticRootS3Boto3Storage"
"""



AWS_ACCESS_KEY_ID = 'ZJDHSVYL4ZD4Y3MGTMML'
AWS_SECRET_ACCESS_KEY = 'C7DQQGL2R5tkD1XBbToaSK2fo9ati4eGtzUFpapDQhc'
AWS_STORAGE_BUCKET_NAME = 'nubebar-assets'
AWS_S3_ENDPOINT_URL = 'https://sfo3.digitaloceanspaces.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'nubebar-static'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_ENDPOINT_URL, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'