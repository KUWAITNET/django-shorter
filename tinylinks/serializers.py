from django.contrib.auth import get_user_model
from django.forms import widgets
from rest_framework import serializers
from tinylinks.models import Tinylink, TinylinkLog
from django.utils import timezone
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    tinylinks = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'tinylinks')


class TinylinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tinylink
        fields = ('id', 'user', 'long_url', 'short_url')
        # 'is_broken', 'validation_error',
        # 'last_checked', 'amount_of_views')


"""
class TinylinkSerializer(serializers.Serializer):
    pk = serializers.Field()  # Note: `Field` is an untyped read-only field.
    #user = serializers.PrimaryKeyRelatedField()
    user = serializers.Field(source='user.username')
    long_url = serializers.CharField(max_length=2500)
    short_url = serializers.CharField(required=False, max_length=32)
    is_broken = serializers.BooleanField(required=False)
    validation_error = serializers.CharField(max_length=100,
            required=False, default='')
    last_checked = serializers.DateTimeField(default=timezone.now(),
            required=False)
    amount_of_views = serializers.IntegerField(default=0)

    def restore_object(self, attrs, instance=None):
        #Create or update a new tinylink instance, given a dictionary
        #of deserialized field values.

        #Note that if we don't define this method, then deserializing
        #data will simply return a dictionary of items.
        if instance:
            # Update existing instance
            #instance.user = attrs.get('user', instance.user)
            instance.long_url = attrs.get('long_url', instance.long_url)
            instance.short_url = attrs.get('short_url', instance.short_url)
            instance.is_broken = attrs.get('is_broken', instance.is_broken)
            instance.validation_error = attrs.get('validation_error', instance.validation_error)
            instance.last_checked = attrs.get('last_checked', instance.last_checked)
            instance.amount_of_views = attrs.get('amount_of_views', instance.amount_of_views)
            return instance

        # Create new instance
        return Tinylink(**attrs)
"""


# class TinylinkLogSerializer(serializers.Serializer):
# pk = serializers.Field()
# tinylink = serializers
