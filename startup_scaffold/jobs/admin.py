from django.contrib import admin
from .models import Job, Skill, JobApplication, Location

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'budget', 'created_at')
    list_filter = ('status', 'location')
    search_fields = ('title', 'description', 'client__email')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'worker', 'applied_at', 'is_hired')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country')
