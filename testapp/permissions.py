from rest_framework.permissions import BasePermission

# Inheritance — BasePermission is the parent class
# We override has_permission() — method overriding

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'teacher')

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                request.user.role == 'student')