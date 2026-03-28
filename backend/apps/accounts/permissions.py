"""Custom permissions for CourseCraft."""

from rest_framework import permissions


class IsInstructor(permissions.BasePermission):
    """Allow access only to users with creator/admin role."""

    message = "You must be an instructor to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("creator", "admin")
        )


class IsStudent(permissions.BasePermission):
    """Allow access only to students."""

    message = "You must be a student to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "student"
        )


class IsAdmin(permissions.BasePermission):
    """Allow access only to platform admins."""

    message = "Admin access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow object modification only to the owner; read access to all authenticated users."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "instructor"):
            return obj.instructor == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "student"):
            return obj.student == request.user
        return False


class IsEnrolledOrInstructor(permissions.BasePermission):
    """Allow access if user is enrolled in the course or is the course instructor."""

    message = "You must be enrolled in this course or be its instructor."

    def has_object_permission(self, request, view, obj):
        user = request.user
        course = getattr(obj, "course", obj)
        if hasattr(course, "instructor") and course.instructor == user:
            return True
        return course.enrollments.filter(student=user, is_active=True).exists()


class IsInstructorOfCourse(permissions.BasePermission):
    """Allow access only to the instructor who owns the course."""

    message = "You must be the instructor of this course."

    def has_object_permission(self, request, view, obj):
        course = getattr(obj, "course", obj)
        return (
            hasattr(course, "instructor")
            and course.instructor == request.user
        )
