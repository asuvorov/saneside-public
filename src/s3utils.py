# http://www.gyford.com/phil/writing/2012/09/26/django-s3-temporary.php

from storages.backends.s3boto import S3BotoStorage

StaticS3BotoStorage = lambda: S3BotoStorage(location="static")
MediaS3BotoStorage = lambda: S3BotoStorage(location="media")
