import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'startup_scaffold.settings')
django.setup()

from accounts.models import CustomUser
from services.models import Skill, Service
from jobs.models import Job, JobApplication

def test_relationships():
    # Check worker-skills relationships
    workers = CustomUser.objects.filter(role='worker')[:3]
    print('=== WORKER-SKILLS RELATIONSHIPS ===')
    for worker in workers:
        skills = worker.skills.all()
        print(f'Worker: {worker.email} has {skills.count()} skills: {[s.name for s in skills]}')

    # Check service-skills relationships
    services = Service.objects.all()[:3]
    print('\n=== SERVICE-SKILLS RELATIONSHIPS ===')
    for service in services:
        skills = service.skills.all()
        print(f'Service: {service.name} requires {skills.count()} skills: {[sk.name for sk in skills]}')

    # Check job-skills relationships
    jobs = Job.objects.all()[:3]
    print('\n=== JOB-SKILLS RELATIONSHIPS ===')
    for job in jobs:
        skills = job.required_skills.all()
        print(f'Job: {job.title} requires {skills.count()} skills: {[s.name for s in skills]}')
        print(f'  Client: {job.client.email}')
        print(f'  Location: {job.location}')
        print(f'  Budget: ${job.budget}')
        print(f'  Status: {job.status}')

    # Check job applications
    applications = JobApplication.objects.all()[:5]
    print('\n=== JOB APPLICATIONS ===')
    for app in applications:
        print(f'Application: {app.worker.email} -> {app.job.title} (Hired: {app.is_hired})')

if __name__ == '__main__':
    test_relationships()
