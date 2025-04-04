# chatbot/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LeaveRequest, Project, Task

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone', 'email', 'is_hr', 'is_manager', 'department', 'is_active')
    list_filter = ('is_hr', 'is_manager', 'is_active', 'department')
    search_fields = ('username', 'phone', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Employment Details', {'fields': ('department', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_hr', 'is_manager', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Authentication State', {'fields': ('auth_state', 'login_attempts', 'last_activity')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'leave_type', 'created_at')
    search_fields = ('employee__username', 'employee__phone')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)  # Only include existing fields

class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'assigned_to', 'due_date', 'status', 'created_at')
    list_filter = ('status', 'project', 'due_date')
    readonly_fields = ('created_at',)  # Only include existing fields

admin.site.register(User, CustomUserAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)
admin.site.register(Project)
admin.site.register(Task, TaskAdmin)