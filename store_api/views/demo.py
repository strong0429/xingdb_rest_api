from django.db import models
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
#from rest_framework.parsers import MultiPartParser, FormParser

from public.utils import handle_api_exception

class File(models.Model):
    logo = models.ImageField(upload_to='logo', null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

class FileView(APIView):
    authentication_classes=()
    permission_classes = ()

    #去掉这个并不影响
    #parser_classes = (MultiPartParser, FormParser)

    def handle_exception(self, exc):
        response = handle_api_exception(exc)
        return Response(response, status=exc.status_code)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data)
        file_serializer.is_valid(raise_exception=True)
        file_serializer.save()
        return Response(file_serializer.data)
