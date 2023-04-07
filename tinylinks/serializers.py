from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from tinylinks.detaults import DEFAULT_ALLOWED_URL_SCHEMES
from tinylinks.models import Tinylink

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    tinylinks = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )

    class Meta:
        model = User
        fields = ("id", "username", "tinylinks")


class TinylinkSerializer(serializers.ModelSerializer):

    short_url = serializers.CharField(read_only=True)

    class Meta:
        model = Tinylink
        fields = ("id", "user", "long_url", "short_url")

    def validate_long_url(self, value):
        url = urlparse(value)
        schemes = getattr(
            settings, "TINYLINK_ALLOWED_URL_SCHEMES", DEFAULT_ALLOWED_URL_SCHEMES
        )
        if url.scheme not in schemes:
            raise serializers.ValidationError(
                _(f"URL scheme must be one of the following: {','.join(schemes)}")
            )
        return value

    def create(self, validated_data):
        user = self.context.get("user", None)
        if not user:
            request = self.context.get("request", None)
            if request:
                user = request.user
        if user and user.is_anonymous:
            user = None
        brothers = Tinylink.objects.filter(
            long_url=validated_data["long_url"], user=user
        )
        if brothers:
            return brothers[0]

        slug = None
        while not slug or Tinylink.objects.filter(short_url=slug):
            slug = get_random_string(getattr(settings, "TINYLINK_LENGTH", 6))

        validated_data["user"] = user
        validated_data["short_url"] = slug
        instance = super().create(validated_data)
        return instance


# class TinylinkSerializer(serializers.Serializer):
#     pk = serializers.Field()  # Note: `Field` is an untyped read-only field.
#     #user = serializers.PrimaryKeyRelatedField()
#     user = serializers.Field(source='user.username')
#     long_url = serializers.CharField(max_length=2500)
#     short_url = serializers.CharField(required=False, max_length=32)
#     is_broken = serializers.BooleanField(required=False)
#     validation_error = serializers.CharField(max_length=100,
#             required=False, default='')
#     last_checked = serializers.DateTimeField(default=timezone.now(),
#             required=False)
#     amount_of_views = serializers.IntegerField(default=0)
#
#     def restore_object(self, attrs, instance=None):
#         #Create or update a new tinylink instance, given a dictionary
#         #of deserialized field values.
#
#         #Note that if we don't define this method, then deserializing
#         #data will simply return a dictionary of items.
#         if instance:
#             # Update existing instance
#             #instance.user = attrs.get('user', instance.user)
#             instance.long_url = attrs.get('long_url', instance.long_url)
#             instance.short_url = attrs.get('short_url', instance.short_url)
#             instance.is_broken = attrs.get('is_broken', instance.is_broken)
#             instance.validation_error = attrs.get('validation_error',
#                                                     instance.validation_error)
#             instance.last_checked = attrs.get('last_checked',
#                                                 instance.last_checked)
#             instance.amount_of_views = attrs.get('amount_of_views',
#                                                 instance.amount_of_views)
#             return instance
#
#         # Create new instance
#         return Tinylink(**attrs)


# class TinylinkLogSerializer(serializers.Serializer):
# pk = serializers.Field()
# tinylink = serializers
