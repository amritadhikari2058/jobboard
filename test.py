from rest_framework.viewsets import ModelViewSet
from jobs.models import Job
from jobs.serializers import JobSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class JobViewSet(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def retrieve_detail(self, request, pk=None):
        job = self.get_object()
        applications = job.application_set.all()

        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    

from rest_framework.routers import DefaultRouter
from applications.views import ApplicationViewSet

router = DefaultRouter()
router.register('applications', ApplicationViewSet)
router.register('jobs', JobViewSet)

urlpatterns = router.urls