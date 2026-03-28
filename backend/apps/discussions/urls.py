from django.urls import path

from . import views

app_name = "discussions"

urlpatterns = [
    # Discussions for a lesson
    path(
        "lessons/<uuid:lesson_id>/",
        views.DiscussionViewSet.as_view({"get": "list", "post": "create"}),
        name="lesson-discussions",
    ),
    path(
        "<uuid:pk>/",
        views.DiscussionViewSet.as_view({
            "get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"
        }),
        name="discussion-detail",
    ),
    path("<uuid:pk>/pin/", views.DiscussionViewSet.as_view({"post": "pin"}), name="discussion-pin"),
    path("<uuid:pk>/resolve/", views.DiscussionViewSet.as_view({"post": "resolve"}), name="discussion-resolve"),
    path("<uuid:pk>/upvote/", views.DiscussionViewSet.as_view({"post": "upvote"}), name="discussion-upvote"),
    # Replies
    path(
        "<uuid:discussion_id>/replies/",
        views.DiscussionReplyViewSet.as_view({"get": "list", "post": "create"}),
        name="discussion-replies",
    ),
    path(
        "<uuid:discussion_id>/replies/<uuid:pk>/",
        views.DiscussionReplyViewSet.as_view({
            "get": "retrieve", "put": "update", "delete": "destroy"
        }),
        name="reply-detail",
    ),
    path(
        "<uuid:discussion_id>/replies/<uuid:pk>/mark-answer/",
        views.DiscussionReplyViewSet.as_view({"post": "mark_answer"}),
        name="reply-mark-answer",
    ),
    path(
        "<uuid:discussion_id>/replies/<uuid:pk>/upvote/",
        views.DiscussionReplyViewSet.as_view({"post": "upvote"}),
        name="reply-upvote",
    ),
]
