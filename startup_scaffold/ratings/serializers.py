from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    # Set queryset to empty initially to avoid assertion error
    reviewer = serializers.PrimaryKeyRelatedField(queryset=Review._meta.get_field('reviewer').related_model.objects.none())
    reviewee = serializers.PrimaryKeyRelatedField(queryset=Review._meta.get_field('reviewee').related_model.objects.none())

    class Meta:
        model = Review
        fields = [
            'id',
            'reviewer',
            'reviewee',
            'job',
            'shift',
            'rating',
            'title',
            'content',
            'is_anonymous',
            'created_at',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        UserModel = self.Meta.model._meta.get_field('reviewer').related_model
        self.fields['reviewer'].queryset = UserModel.objects.all()
        self.fields['reviewee'].queryset = UserModel.objects.all()
