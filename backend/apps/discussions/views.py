from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsInstructorOfCourse

from .models import Discussion, DiscussionReply
from .serializers import (
    DiscussionCreateSerializer,
    DiscussionReplyCreateSerializer,
    DiscussionReplySerializer,
    DiscussionSerializer,
)


class DiscussionViewSet(viewsets.ModelViewSet):
    """CRUD for discussion threads within a lesson."""

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.IsAuthenticated()]
        if self.action in ("pin", "resolve", "destroy"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ("create",):
            return DiscussionCreateSerializer
        return DiscussionSerializer

    def get_queryset(self):
        lesson_id = self.kwargs.get("lesson_id")
        qs = Discussion.objects.select_related("author")
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs.prefetch_related("replies__author", "replies__children__author")

    @action(detail=True, methods=["post"])
    def pin(self, request, **kwargs):
        """Pin/unpin a discussion - instructor only."""
        discussion = self.get_object()
        discussion.is_pinned = not discussion.is_pinned
        discussion.save(update_fields=["is_pinned"])
        action_text = "pinned" if discussion.is_pinned else "unpinned"
        return Response({"detail": f"Discussion {action_text}.", "is_pinned": discussion.is_pinned})

    @action(detail=True, methods=["post"])
    def resolve(self, request, **kwargs):
        """Mark a discussion as resolved."""
        discussion = self.get_object()
        discussion.is_resolved = True
        discussion.save(update_fields=["is_resolved"])
        return Response({"detail": "Discussion marked as resolved."})

    @action(detail=True, methods=["post"])
    def upvote(self, request, **kwargs):
        """Upvote a discussion."""
        discussion = self.get_object()
        discussion.upvote_count += 1
        discussion.save(update_fields=["upvote_count"])
        return Response({"upvote_count": discussion.upvote_count})


class DiscussionReplyViewSet(viewsets.ModelViewSet):
    """CRUD for replies within a discussion."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create",):
            return DiscussionReplyCreateSerializer
        return DiscussionReplySerializer

    def get_queryset(self):
        discussion_id = self.kwargs.get("discussion_id")
        return DiscussionReply.objects.filter(
            discussion_id=discussion_id, parent__isnull=True
        ).select_related("author").prefetch_related("children__author")

    @action(detail=True, methods=["post"])
    def mark_answer(self, request, **kwargs):
        """Mark a reply as the accepted answer - instructor only."""
        reply = self.get_object()
        DiscussionReply.objects.filter(
            discussion=reply.discussion, is_answer=True
        ).update(is_answer=False)
        reply.is_answer = True
        reply.save(update_fields=["is_answer"])
        reply.discussion.is_resolved = True
        reply.discussion.save(update_fields=["is_resolved"])
        return Response({"detail": "Reply marked as accepted answer."})

    @action(detail=True, methods=["post"])
    def upvote(self, request, **kwargs):
        """Upvote a reply."""
        reply = self.get_object()
        reply.upvote_count += 1
        reply.save(update_fields=["upvote_count"])
        return Response({"upvote_count": reply.upvote_count})
