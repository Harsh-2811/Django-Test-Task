from rest_framework import serializers
from api.csv_manager.models import Employee

class CSVUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()

class ResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class QuerySerializer(serializers.Serializer):
    employee_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    hire_date = serializers.DateField(required=False)

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        extra_kwargs = {
            "source_file": {"write_only": True},
        }