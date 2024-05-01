from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    EDIT_METHODS = ('PATCH')

    def has_permission(self, request, view):
        return request.user.role == 1
