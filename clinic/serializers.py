from rest_framework import serializers
import os


class GetParameters(serializers.Serializer):
    params = serializers.CharField(required=True)
    
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith('.zip'):
            raise serializers.ValidationError('Only ZIP files are supported')
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError('File size exceeds 50MB limit')
        return value

class FileProcessingSerializer(serializers.Serializer):
    file_path = serializers.CharField(max_length=500)

    def validate_file_path(self, value):
        if not os.path.exists(value):
            raise serializers.ValidationError('File path does not exist')
        return value