from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from portal.models import Project, Task

@login_required 
def index(request):

    user = request.user
    context = {"user":user}
    # check staff or employee
    if (request.user.is_staff):
        # staff

        return render(request, "portal/dashboards/staff.html", context)
    else:
        # employee
        context.update({"tasks":user.tasks.all()})
        
        # print(user.tasks.all())
        return render(request, "portal/dashboards/employee.html", context)

def login(request):

    context = {}
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, employee_id=employee_id, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")  # go to home page after login
        else:
            context["error"] = "Invalid Employee ID or password"

    # GET request or failed login
    return render(request, "portal/auth/login.html", context)

@login_required
def logout(request):

    auth_logout(request)
    return redirect("index")

@login_required
def task(request,id):
    task = get_object_or_404(Task,id=id)
    return render(request,"portal/pages/task.html",{
        "task":task
    })

@login_required
def project(request,id):
    project = get_object_or_404(Project,id=id)
    return render(request,"portal/pages/project.html",{
        "project":project,
        "tasks":project.tasks.all()
                                                       })