from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class Employee(AbstractUser):
    employee_id = models.CharField(max_length=20, unique=True,db_index=True)

    USERNAME_FIELD = "employee_id"   # tell Django to use employee_id for login
    REQUIRED_FIELDS = ["username"]   # keep username also required if you want

    def __str__(self):
        return f"{self.username} ({self.employee_id})"


# Project Model
class Project(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_by = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Task Model
class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey("Employee", on_delete=models.CASCADE,related_name="tasks")
    deadline = models.DateTimeField()
    is_complete = models.BooleanField(default=False)  # default added False
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
