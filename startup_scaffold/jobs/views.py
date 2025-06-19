from rest_framework import viewsets, permissions, status, throttling
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, Skill, Location, JobApplication, JobRecommendation
from .serializers import JobSerializer, SkillSerializer, LocationSerializer, JobApplicationSerializer, JobRecommendationSerializer

class IsJobOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a job to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the job or admins.
        return obj.client == request.user or request.user.is_staff

class JobCreationThrottle(throttling.UserRateThrottle):
    scope = 'job_creation'

class ApplicationThrottle(throttling.UserRateThrottle):
    scope = 'application'

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsJobOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'required_skills__name': ['icontains'],
        'budget': ['gte', 'lte'],
        'location__city': ['icontains'],
        'status': ['exact'],
        'client__ratings__rating': ['gte'],
    }
    throttle_classes = [JobCreationThrottle]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Job.objects.all()
        return Job.objects.filter(Q(client=user) | Q(status=Job.Status.OPEN))

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my(self, request):
        """Jobs posted by the current user (client)"""
        jobs = Job.objects.filter(client=request.user)
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recommended(self, request):
        """Jobs recommended for the current user (worker)"""
        user = request.user
        recommended_jobs = Job.objects.filter(
            required_skills__in=user.skills.all(),
            location__in=[user.profile.location] if hasattr(user, 'profile') else [],
            status=Job.Status.OPEN
        ).exclude(applications__worker=user).distinct()
        serializer = self.get_serializer(recommended_jobs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def applied(self, request):
        """Jobs the current user (worker) has applied to"""
        applications = JobApplication.objects.filter(worker=request.user)
        jobs = Job.objects.filter(applications__in=applications)
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def hire(self, request, pk=None):
        """Endpoint for client to hire a worker for a job"""
        job = self.get_object()
        if job.client != request.user and not request.user.is_staff:
            return Response({'detail': 'Not authorized to hire for this job.'}, status=status.HTTP_403_FORBIDDEN)

        worker_id = request.data.get('worker_id')
        if not worker_id:
            return Response({'detail': 'worker_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            application = JobApplication.objects.get(job=job, worker__id=worker_id)
        except JobApplication.DoesNotExist:
            return Response({'detail': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Prevent hiring more than max_workers
        hired_count = JobApplication.objects.filter(job=job, is_hired=True).count()
        if hired_count >= job.max_workers:
            return Response({'detail': 'Maximum number of workers already hired for this job.'}, status=status.HTTP_400_BAD_REQUEST)

        application.is_hired = True
        application.save()

        # Update job status if max_workers reached
        if hired_count + 1 >= job.max_workers:
            job.status = Job.Status.IN_PROGRESS
            job.save()

        return Response({'detail': f'Worker {application.worker.email} hired for job {job.title}.'})

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ApplicationThrottle]

    def perform_create(self, serializer):
        job = serializer.validated_data.get('job')
        if job.status != Job.Status.OPEN:
            raise permissions.PermissionDenied("Cannot apply to a job that is not open.")
        serializer.save()

class JobRecommendationViewSet(viewsets.ModelViewSet):
    queryset = JobRecommendation.objects.all()
    serializer_class = JobRecommendationSerializer
    permission_classes = [IsAuthenticated]
