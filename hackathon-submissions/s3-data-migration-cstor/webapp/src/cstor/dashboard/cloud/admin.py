from django.contrib import admin


from .models import CloudProvider, Bucket, Task, Migration

# Register your models here.
admin.site.register(CloudProvider)
admin.site.register(Bucket)
admin.site.register(Task)
admin.site.register(Migration)
