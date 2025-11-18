from typing import Any

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее изменять объект только его создателю.
    """
    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "creator", None) == getattr(request, "user", None)
