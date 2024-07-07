from django.db import models

# Create your models here.
class Employee(models.Model):
    employee_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    hire_date = models.DateField()
    job_id = models.CharField(max_length=10)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    commission_pct = models.DecimalField(max_digits=10, decimal_places=2)
    manager_id = models.IntegerField()
    department_id = models.IntegerField()
    def __str__(self):
        return str(self.employee_id) + " - " + self.first_name + " " + self.last_name