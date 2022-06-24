"""Cloud Serializers"""
from rest_framework import serializers

from .models import CloudProvider, Bucket, Task, Migration


class CloudProviderListSerializer(serializers.ModelSerializer):
    """CloudProviderList view"""
    class Meta:
        model = CloudProvider
        fields = (
            "id",
            "name",
            "description",
            "cloud_name",
            "cloud_access_key",
            "cloud_endpoint",
            "cloud_cred_valid",
        )


class TaskSerializer(serializers.ModelSerializer):
    """TaskSerializer"""
    class Meta:
        model = Task
        fields = (
            "id",
            "uuid",
            "category",
            "retries",
            "status",
            "request_args",
            "result_ok",
            "result_error"
        )


class BucketListSerializer(serializers.ModelSerializer):
    """BucketList view"""
    cloud_provider = CloudProviderListSerializer(read_only=True)

    class Meta:
        model = Bucket
        fields = (
            "id",
            "name",
            "description",
            "cloud_provider",
            "cloud_region",
        )


class MigrationListSerializer(serializers.ModelSerializer):
    """BucketList view"""
    src_bucket = BucketListSerializer(read_only=True)
    dest_bucket = BucketListSerializer(read_only=True)

    class Meta:
        model = Migration
        fields = (
            "id",
            "name",
            "description",
            "uuid",
            "src_bucket",
            "src_prefix",
            "dest_bucket",
            "dest_prefix",
            "status",
            # Filter Options
            "filter_date_before",
            "filter_date_after",
            "filter_size_gte",
            "filter_size_lte",
            # Progress
            "total_count",
            "total_size",
            "progress_count",
            "progress_size",
            "success_count",
            "success_size",
            "fail_count",
            "fail_size",
            "status",
        )
