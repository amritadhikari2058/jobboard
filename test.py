from rest_framework import serializers
from jobs.models import Job
from applications.models import Application
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['title', 'location']

@api_view
def job_detail(request, id):
    job = Job.objects.get(id=id)
    serializer = JobSerializer(job)

    return Response(serializer.data)


@api_view(['POST'])
def create_job(request):
    serializer = JobSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors)


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['title', 'location']
    
    def validate_title(self, value):
        if len(value)<3:
            raise serializers.ValidationError('Title too short.')
        
        return value


class JobSerializer(serializers.ModelSerializer):
    recruiter_email = serializers.EmailField(source='user.email')

    class Meta:
        model = Job
        fields = ['title', 'location', 'recruiter_email']


class ApplicationSerialiser(serializers.ModelSerializer):
    class Meta:
        model=Application
        fields=['id', 'status']

class JobSerializer(serializers.ModelSerializer):
    applications= ApplicationSerialiser(source='user.email')

    class Meta:
        model = Job
        fields=['title', 'applications']


class JobSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Job
        fields = '__all__'