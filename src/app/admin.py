from django.contrib import admin

from djangoseo.admin import register_seo_admin

from app.seo import Metadata

register_seo_admin(admin.site, Metadata)
