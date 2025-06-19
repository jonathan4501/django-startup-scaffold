from rest_framework import serializers

class TimeStampedSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class UUIDSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

class DynamicFieldsMixin(serializers.Serializer):
    """
    A Serializer mixin that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
