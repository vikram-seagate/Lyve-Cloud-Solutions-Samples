"""Django Models"""
import json
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Task(models.Model):
    """Task"""

    class TaskStatus(models.IntegerChoices):
        """Task Status"""
        PROGRESS_UPDATE = 0
        PENDING = 1
        COMPLETED = 2
        FAILED = 3
        RETRYING = 4

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    category = models.CharField(max_length=100)
    retries = models.IntegerField(default=0)
    status = models.IntegerField(
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
    )
    request_args = models.TextField()
    result_ok = models.TextField(blank=True, null=True)
    result_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="task",
        on_delete=models.CASCADE,
    )


class CloudProvider(models.Model):
    """Cloud Provider"""

    class SupportedProvider(models.TextChoices):
        """Supported Cloud Providers"""
        AWS = "AWS", _("Amazon Web Services")
        LYC = "LYC", _("Lyve Cloud by Seagate")

    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    cloud_name = models.CharField(
        max_length=5,
        choices=SupportedProvider.choices,
        default=SupportedProvider.AWS,
    )
    # Last 6 Characters of Access Key
    cloud_access_key = models.CharField(max_length=255)
    cloud_endpoint = models.URLField(max_length=200, blank=True, null=True)
    cloud_region = models.CharField(max_length=32, blank=True, null=True)
    cloud_cred_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    cloud_cred_arn = models.TextField(blank=True, null=True)
    cloud_cred_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="cloud_provider",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Str Representation"""
        return f"{self.cloud_name}:{self.name}"

    class Meta:
        ordering = ("created_at",)

    def save(self, *args, **kwargs):
        """
        Send and create a task as well
        """
        super(CloudProvider, self).save(*args, **kwargs)


class Bucket(models.Model):
    """Cloud Bucket"""
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    cloud_region = models.CharField(max_length=32, blank=True, null=True)
    cloud_provider = models.OneToOneField(
        CloudProvider,
        on_delete=models.CASCADE,
    )
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="cloud_bucket",
        on_delete=models.CASCADE,
    )


class Migration(models.Model):
    """Migration"""
    class MigrationStatus(models.IntegerChoices):
        """Task Status"""
        SCANNING = 0
        RUNNING = 1
        PAUSED = 2
        COMPLETED = 3
        FAILED = 4
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    src_bucket = models.ForeignKey(
        Bucket,
        on_delete=models.RESTRICT,
        related_name="src_bucket",
    )
    src_prefix = models.CharField(max_length=255, default="", blank=True)
    dest_bucket = models.ForeignKey(
        Bucket,
        on_delete=models.RESTRICT,
        related_name="dest_bucket",
    )
    dest_prefix = models.CharField(max_length=255, default="", blank=True)

    # Filter Options
    filter_date_before = models.CharField(max_length=16, default="", blank=True)
    filter_date_after = models.CharField(max_length=16, default="", blank=True)
    filter_size_gte = models.IntegerField(default=0, blank=True)
    filter_size_lte = models.IntegerField(default=0, blank=True)
    # Progress
    total_count = models.IntegerField(default=0)
    total_size = models.IntegerField(default=0)  # in bytes
    progress_count = models.IntegerField(default=0)
    progress_size = models.IntegerField(default=0)  # in bytes
    success_count = models.IntegerField(default=0)
    success_size = models.IntegerField(default=0)  # in bytes
    fail_count = models.IntegerField(default=0)
    fail_size = models.IntegerField(default=0)  # in bytes
    # Status
    max_workers = models.IntegerField(default=5)  # max number of workers
    status = models.IntegerField(
        choices=MigrationStatus.choices,
        default=MigrationStatus.SCANNING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="migration",
        on_delete=models.CASCADE,
    )
