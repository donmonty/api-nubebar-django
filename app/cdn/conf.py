import os

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