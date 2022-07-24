""" cloud/permissions.py """
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Only allow if the request user is the owner
    """
    def has_object_permission(self, request, view, obj):
        """Check permission"""
        return obj.created_by == request.user
