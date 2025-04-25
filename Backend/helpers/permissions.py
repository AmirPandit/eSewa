# accounts/permissions.py

from rest_framework.permissions import BasePermission

class RoleBasedPermission(BasePermission):
    """
    Custom permission to only allow users with certain roles to access the view.
    """
    def __init__(self, roles=None):
        self.roles = roles or []

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role in self.roles:
            return True
        return False