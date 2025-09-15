from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from portal.models import Project, Task
@login_required 
def index(request):
    user = request.user
    context = {"user": user}
    
    # check staff or employee
    if (request.user.is_staff):
        # staff
        return redirect("/admin/")
    else:
        # employee
        tasks = user.tasks.all()
        
        # Get filter and sort parameters
        project_filter = request.GET.get('project')
        sort_by = request.GET.get('sort', 'deadline')  # default sort by deadline
        order = request.GET.get('order', 'asc')  # default ascending
        
        # Apply project filter
        if project_filter:
            tasks = tasks.filter(project_id=project_filter)
        
        # Apply sorting
        if sort_by == 'deadline':
            if order == 'desc':
                tasks = tasks.order_by('-deadline')
            else:
                tasks = tasks.order_by('deadline')
        
        # Get all projects for the filter dropdown
        user_projects = Project.objects.filter(tasks__assigned_to=user).distinct()
        
        # Pagination
        paginator = Paginator(tasks, 10)  # Show 10 tasks per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            "tasks": page_obj,
            "user_projects": user_projects,
            "current_project": project_filter,
            "current_sort": sort_by,
            "current_order": order,
        })
        
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