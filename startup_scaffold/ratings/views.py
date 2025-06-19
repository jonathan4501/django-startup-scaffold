from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer
from jobs.models import Job
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Enforce business logic: no self-review, job completed, user involved
        reviewer = self.request.user
        reviewee = serializer.validated_data.get('reviewee')
        job = serializer.validated_data.get('job')

        if reviewer == reviewee:
            raise serializers.ValidationError("You cannot review yourself.")

        if job:
            # Check if job is completed and user involved
            if job.status != 'completed':
                raise serializers.ValidationError("Cannot review a job that is not completed.")
            if reviewer not in [job.worker, job.client] or reviewee not in [job.worker, job.client]:
                raise serializers.ValidationError("Reviewer and reviewee must be involved in the job.")

        serializer.save(reviewer=reviewer)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/reviews')
    def reviews_received(self, request, user_id=None):
        user = get_object_or_404(User, pk=user_id)
        reviews = Review.objects.filter(reviewee=user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/ratings/average')
    def average_rating(self, request, user_id=None):
        user = get_object_or_404(User, pk=user_id)
        avg_rating = Review.objects.filter(reviewee=user).aggregate(Avg('rating'))['rating__avg']
        return Response({'user_id': str(user.id), 'average_rating': avg_rating})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_review_for_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    user = request.user

    # Check job completion and user involvement
    if job.status != 'completed':
        return Response({"detail": "Cannot review a job that is not completed."}, status=status.HTTP_400_BAD_REQUEST)
    if user not in [job.worker, job.client]:
        return Response({"detail": "You are not involved in this job."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data['reviewer'] = str(user.id)
    # Determine reviewee: the other party in the job
    if user == job.worker:
        data['reviewee'] = str(job.client.id)
    else:
        data['reviewee'] = str(job.worker.id)
    data['job'] = str(job.id)

    serializer = ReviewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
