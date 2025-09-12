from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Employee, Project, Task


# Enhanced Employee Admin
class EmployeeAdmin(UserAdmin):
    model = Employee
    
    # What fields to display in the list view
    list_display = ('employee_id', 'username', 'first_name', 'last_name', 
                   'email', 'is_active', 'is_staff', 'date_joined', 'project_count', 'task_count')
    
    # Add search functionality
    search_fields = ('employee_id', 'username', 'first_name', 'last_name', 'email')
    
    # Add filters in the right sidebar
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    
    # Make some fields clickable links
    list_display_links = ('employee_id', 'username')
    
    # Add employee_id to the admin forms
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Info', {'fields': ('employee_id',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Employee Info', {'fields': ('employee_id',)}),
    )
    
    # Custom methods to show counts
    def project_count(self, obj):
        count = obj.projects.count()
        if count > 0:
            url = reverse('admin:portal_project_changelist') + f'?created_by__id__exact={obj.id}'
            return format_html('<a href="{}">{} projects</a>', url, count)
        return count
    project_count.short_description = 'Projects Created'
    
    def task_count(self, obj):
        count = obj.tasks.count()
        if count > 0:
            url = reverse('admin:portal_task_changelist') + f'?assigned_to__id__exact={obj.id}'
            return format_html('<a href="{}">{} tasks</a>', url, count)
        return count
    task_count.short_description = 'Tasks Assigned'


# Inline for Tasks within Project admin
class TaskInline(admin.TabularInline):
    model = Task
    extra = 1  # Number of empty forms to display
    fields = ('title', 'assigned_to', 'deadline', 'is_complete')
    
    # Make it more compact
    classes = ['collapse']  # Makes it collapsible


# Enhanced Project Admin
class ProjectAdmin(admin.ModelAdmin):
    # Fields to display in list view
    list_display = ('title', 'created_by', 'deadline', 'created_at', 'task_count', 'completed_tasks', 'progress_bar')
    
    # Add search
    search_fields = ('title', 'description', 'created_by__username', 'created_by__employee_id')
    
    # Add filters
    list_filter = ('created_at', 'deadline', 'created_by')
    
    # Add date hierarchy navigation
    date_hierarchy = 'deadline'
    
    # Order by deadline by default
    ordering = ('deadline',)
    
    # Make title clickable
    list_display_links = ('title',)
    
    # Organize form fields into sections
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'description')
        }),
        ('Timeline', {
            'fields': ('deadline',),
            'classes': ('wide',)
        }),
        ('Assignment', {
            'fields': ('created_by',),
        }),
    )
    
    # Show related tasks inline
    inlines = [TaskInline]
    
    # Custom methods for additional info
    def task_count(self, obj):
        count = obj.tasks.count()
        if count > 0:
            url = reverse('admin:portal_task_changelist') + f'?project__id__exact={obj.id}'
            return format_html('<a href="{}">{} tasks</a>', url, count)
        return count
    task_count.short_description = 'Total Tasks'
    
    def completed_tasks(self, obj):
        completed = obj.tasks.filter(is_complete=True).count()
        total = obj.tasks.count()
        return f"{completed}/{total}"
    completed_tasks.short_description = 'Completed'
    
    def progress_bar(self, obj):
        total_tasks = obj.tasks.count()
        if total_tasks == 0:
            return "No tasks"
        
        completed_tasks = obj.tasks.filter(is_complete=True).count()
        progress = int((completed_tasks / total_tasks) * 100)
        
        color = 'green' if progress == 100 else 'orange' if progress >= 50 else 'red'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%'
            '</div></div>',
            progress, color, progress
        )
    progress_bar.short_description = 'Progress'


# Enhanced Task Admin
class TaskAdmin(admin.ModelAdmin):
    # List display
    list_display = ('title', 'project_link', 'assigned_to', 'deadline', 'is_complete', 'created_at', 'status_color')
    
    # Search functionality
    search_fields = ('title', 'description', 'project__title', 'assigned_to__username', 'assigned_to__employee_id')
    
    # Filters
    list_filter = ('is_complete', 'deadline', 'created_at', 'project', 'assigned_to')
    
    # Date navigation
    date_hierarchy = 'deadline'
    
    # Default ordering
    ordering = ('deadline', 'is_complete')
    
    # Clickable fields
    list_display_links = ('title',)
    
    # Enable bulk actions
    list_editable = ('is_complete',)
    
    # Organize form fields
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description')
        }),
        ('Assignment', {
            'fields': ('project', 'assigned_to'),
            'classes': ('wide',)
        }),
        ('Timeline & Status', {
            'fields': ('deadline', 'is_complete'),
            'classes': ('wide',)
        }),
    )
    
    # Custom methods
    def project_link(self, obj):
        url = reverse('admin:portal_project_change', args=[obj.project.id])
        return format_html('<a href="{}">{}</a>', url, obj.project.title)
    project_link.short_description = 'Project'
    project_link.admin_order_field = 'project__title'
    
    def status_color(self, obj):
        if obj.is_complete:
            return format_html('<span style="color: green; font-weight: bold;">✓ Complete</span>')
        elif obj.deadline and obj.deadline < timezone.now():
            return format_html('<span style="color: red; font-weight: bold;">⚠ Overdue</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⏳ Pending</span>')
    status_color.short_description = 'Status'
    
    # Custom actions
    actions = ['mark_complete', 'mark_incomplete']
    
    def mark_complete(self, request, queryset):
        updated = queryset.update(is_complete=True)
        self.message_user(request, f'{updated} tasks marked as complete.')
    mark_complete.short_description = "Mark selected tasks as complete"
    
    def mark_incomplete(self, request, queryset):
        updated = queryset.update(is_complete=False)
        self.message_user(request, f'{updated} tasks marked as incomplete.')
    mark_incomplete.short_description = "Mark selected tasks as incomplete"


# Register models with enhanced admin classes
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)


# Customize admin site headers
admin.site.site_header = "Project Management Admin"
admin.site.site_title = "PM Admin"
admin.site.index_title = "Welcome to Project Management System"