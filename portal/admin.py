from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Project, Task

class EmployeeAdmin(UserAdmin):
    model = Employee
    # Add employee_id into the admin forms
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('employee_id',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('employee_id',)}),
    )

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Project)
admin.site.register(Task)
