from rest_framework import serializers
from api.csv_manager.models import Employee
from rest_framework.exceptions import ValidationError

def file_size_validator(file):
    max_size_mb = 5  # Maximum file size in megabytes
    max_size = max_size_mb * 1024 * 1024  # Convert to bytes

    if file.size > max_size:
        raise ValidationError(f"File size should not exceed {max_size_mb} MB.")

class CSVUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField(validators=[file_size_validator])

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