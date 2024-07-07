import csv
from django.shortcuts import render
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser
from api.csv_manager.serializers import CSVUploadSerializer, ResponseSerializer, QuerySerializer, EmployeeSerializer
from rest_framework.response import Response
from api.csv_manager.models import Employee
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import date
from dateutil import parser
from django.db.models import Q, Max, Min, Avg


# Create your views here.

class UploadCSVView(GenericAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = CSVUploadSerializer

    def parse_date(self, date_string):
        date = parser.parse(date_string)
        return date.strftime('%Y-%m-%d')
    
    def create_employees(self, data, csv_file):
        employees = []
        for row in data:
            employee = Employee(
                employee_id=row["EMPLOYEE_ID"],
                first_name=row["FIRST_NAME"],
                last_name=row["LAST_NAME"],
                email=row["EMAIL"],
                phone_number=row["PHONE_NUMBER"],
                hire_date=self.parse_date(row["HIRE_DATE"]),
                job_id=row["JOB_ID"],
                salary=row["SALARY"],
                commission_pct=row["COMMISSION_PCT"] if str(row["COMMISSION_PCT"]).strip() != "-" else 0,
                manager_id=row["MANAGER_ID"] if str(row["MANAGER_ID"]).strip() != "-" else 0,
                department_id=row["DEPARTMENT_ID"],
            )
            employees.append(employee)
        return employees
    
    @extend_schema(
        request=CSVUploadSerializer,
        responses={
            201: ResponseSerializer,
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            csv_file = serializer.validated_data["csv_file"]
            csv_data = csv_file.read().decode('utf-8')
            csv_lines = csv_data.split('\n')

            data = csv.DictReader(csv_lines)
            employees = self.create_employees(data, csv_file)
            Employee.objects.bulk_create(employees)
                
            # Do something with the csv_file
            return Response({"message": "File uploaded successfully"}, status=201)

class SearchView(ListAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def get_queryset(self):
        query_params = self.request.query_params
        employee_id = query_params.get("employee_id")
        name = query_params.get("name")
        email = query_params.get("email")
        hire_date = query_params.get("hire_date")

        min_hire_date = query_params.get("min_hire_date")
        max_hire_date = query_params.get("max_hire_date")

        operation = query_params.get("operation")

        if employee_id:
            return Employee.objects.filter(employee_id=employee_id)
        if name:
            return Employee.objects.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name)).distinct()
        if email:
            return Employee.objects.filter(email=email)
        if hire_date:
            return Employee.objects.filter(hire_date=hire_date)
        
        if min_hire_date and max_hire_date:
            return Employee.objects.filter(hire_date__range=[min_hire_date, max_hire_date])
        if min_hire_date:
            return Employee.objects.filter(hire_date__gte=min_hire_date)
        if max_hire_date:
            return Employee.objects.filter(hire_date__lte=max_hire_date)

        if operation == "min":
            min_salary = Employee.objects.aggregate(Min("salary"))["salary__min"]
            return Employee.objects.filter(salary=min_salary)
        if operation == "max":
            max_salary = Employee.objects.aggregate(Max("salary"))["salary__max"]
            return Employee.objects.filter(salary=max_salary)
        if operation == "mean":
            avg_salary = Employee.objects.aggregate(Avg("salary"))["salary__avg"]
            return Employee.objects.filter(salary=avg_salary)
        
        return super().get_queryset()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="employee_id", type=int, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="name", type=str, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="email", type=str, location=OpenApiParameter.QUERY, required=False),
            OpenApiParameter(name="hire_date", type=date, location=OpenApiParameter.QUERY, required=False, description="Date format: YYYY-MM-DD", pattern=r"\d{4}-\d{2}-\d{2}"),
            OpenApiParameter(name="max_hire_date", type=date, location=OpenApiParameter.QUERY, required=False, description="Date format: YYYY-MM-DD", pattern=r"\d{4}-\d{2}-\d{2}"),
            OpenApiParameter(name="min_hire_date", type=date, location=OpenApiParameter.QUERY, required=False, description="Date format: YYYY-MM-DD", pattern=r"\d{4}-\d{2}-\d{2}"),
            OpenApiParameter(name="operation", type=str, location=OpenApiParameter.QUERY, required=False, description="Operation to perform. Available operations: min, max, mean. For example Min will return employees with minimum salary"),
        ],
        responses={
            200: EmployeeSerializer(many=True),
        }
    )
    def get(self, request):
        return self.list(request)