from rest_framework import serializers

class NewsSerializer(serializers.Serializer):
    headline = serializers.CharField()
    link = serializers.CharField()
    source = serializers.CharField()
