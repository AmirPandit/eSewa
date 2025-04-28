from rest_framework import serializers
from .models import ChatRoom, RoomMembership, Message
from accounts.serializers import UserSerializer
from accounts.models import CustomUser
class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['is_member'] = instance.memberships.filter(user=self.context['request'].user).exists()
        ret['members_count'] = instance.memberships.count()
        return ret

class RoomMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMembership
        fields = ['id', 'user', 'room', 'joined_at']
        read_only_fields = ['id', 'joined_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'timestamp', 'sender']

    
# class MessageCassendraSerializer(serializers.Serializer):
#     id = serializers.UUIDField(read_only=True)
#     room_id = serializers.UUIDField()
#     sender_id = serializers.UUIDField(read_only=True)
#     content = serializers.CharField()
#     document = serializers.CharField(allow_null=True)
#     timestamp = serializers.DateTimeField(read_only=True)

#     def create(self, validated_data):
#         return Message.create(**validated_data)

#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         # You'll need to fetch the user from PostgreSQL
#         user = CustomUser.objects.get(id=instance.sender_id)
#         ret['sender'] = UserSerializer(user).data
#         return ret