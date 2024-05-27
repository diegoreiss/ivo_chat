from rest_framework import serializers


class ChatMessageDataButtonsSerializer(serializers.Serializer):
    title = serializers.CharField()
    payload = serializers.CharField()

class ChatMessageDataSerializer(serializers.Serializer):
    elements = serializers.ListField(child=serializers.JSONField())
    quick_replies = serializers.ListField(child=serializers.JSONField())
    buttons = serializers.ListField(child=ChatMessageDataButtonsSerializer())
    attachment = serializers.ListField(child=serializers.JSONField())
    image = serializers.ListField(child=serializers.JSONField())
    custom = serializers.ListField(child=serializers.JSONField())


class ChatMessageSerializer(serializers.Serializer):
    timestamp = serializers.FloatField()
    sender = serializers.BooleanField()
    spinnerLoading = serializers.BooleanField()
    bot_should_respond = serializers.BooleanField()
    type = serializers.CharField()
    message = serializers.CharField()
    data = ChatMessageDataSerializer()
