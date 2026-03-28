from rest_framework import serializers

from .models import Discussion, DiscussionReply


class DiscussionReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    author_avatar = serializers.ImageField(source="author.avatar", read_only=True)
    author_role = serializers.CharField(source="author.role", read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionReply
        fields = (
            "id", "discussion", "author_name", "author_avatar", "author_role",
            "body", "is_answer", "upvote_count", "parent",
            "children", "created_at", "updated_at",
        )
        read_only_fields = ("id", "is_answer", "upvote_count", "created_at", "updated_at")

    def get_children(self, obj):
        children = obj.children.select_related("author").all()
        return DiscussionReplySerializer(children, many=True).data


class DiscussionReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionReply
        fields = ("id", "discussion", "body", "parent")
        read_only_fields = ("id",)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class DiscussionSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    author_avatar = serializers.ImageField(source="author.avatar", read_only=True)
    replies = DiscussionReplySerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = (
            "id", "lesson", "author_name", "author_avatar",
            "title", "body", "is_pinned", "is_resolved",
            "upvote_count", "reply_count", "replies",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "is_pinned", "is_resolved", "upvote_count",
            "reply_count", "created_at", "updated_at",
        )


class DiscussionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ("id", "lesson", "title", "body")
        read_only_fields = ("id",)

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
