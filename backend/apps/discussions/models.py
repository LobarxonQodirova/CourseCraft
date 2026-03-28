import uuid

from django.conf import settings
from django.db import models


class Discussion(models.Model):
    """A discussion thread within a course lesson."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(
        "courses.Lesson", on_delete=models.CASCADE, related_name="discussions"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discussions"
    )
    title = models.CharField(max_length=300)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    upvote_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "discussions"
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["lesson", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} (by {self.author.display_name})"


class DiscussionReply(models.Model):
    """A reply to a discussion thread."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(
        Discussion, on_delete=models.CASCADE, related_name="replies"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discussion_replies"
    )
    body = models.TextField()
    is_answer = models.BooleanField(
        default=False, help_text="Marked as the accepted answer by instructor"
    )
    upvote_count = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "discussion_replies"
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by {self.author.display_name} on '{self.discussion.title}'"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.discussion.reply_count = self.discussion.replies.count()
            self.discussion.save(update_fields=["reply_count"])
