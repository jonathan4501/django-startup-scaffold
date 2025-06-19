from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from services.models import Skill, Service
from jobs.models import Location, Job, JobApplication
from .factories.accounts import UserFactory, AdminFactory, WorkerFactory, ClientFactory
from .factories.services import SkillFactory, ServiceFactory
from .factories.jobs import LocationFactory, JobFactory, JobApplicationFactory

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)'
        )
        parser.add_argument(
            '--skills',
            type=int,
            default=20,
            help='Number of skills to create (default: 20)'
        )
        parser.add_argument(
            '--services',
            type=int,
            default=15,
            help='Number of services to create (default: 15)'
        )
        parser.add_argument(
            '--locations',
            type=int,
            default=10,
            help='Number of locations to create (default: 10)'
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=30,
            help='Number of jobs to create (default: 30)'
        )
        parser.add_argument(
            '--applications',
            type=int,
            default=100,
            help='Number of job applications to create (default: 100)'
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['users', 'skills', 'services', 'locations', 'jobs', 'applications', 'all'],
            default='all',
            help='Specific model to seed (default: all)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        with transaction.atomic():
            if options['model'] == 'all':
                self.seed_all(options)
            elif options['model'] == 'users':
                self.seed_users(options['users'])
            elif options['model'] == 'skills':
                self.seed_skills(options['skills'])
            elif options['model'] == 'services':
                self.seed_services(options['services'])
            elif options['model'] == 'locations':
                self.seed_locations(options['locations'])
            elif options['model'] == 'jobs':
                self.seed_jobs(options['jobs'])
            elif options['model'] == 'applications':
                self.seed_applications(options['applications'])

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded the database!')
        )

    def clear_data(self):
        self.stdout.write('Clearing existing data...')
        JobApplication.objects.all().delete()
        Job.objects.all().delete()
        Location.objects.all().delete()
        Service.objects.all().delete()
        Skill.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('Data cleared!'))

    def seed_all(self, options):
        # Create skills first so they're available for users
        self.seed_skills(options['skills'])
        self.seed_users(options['users'])
        self.seed_services(options['services'])
        self.seed_locations(options['locations'])
        self.seed_jobs(options['jobs'])
        self.seed_applications(options['applications'])

    def seed_users(self, count):
        self.stdout.write(f'Creating {count} users...')
        
        # Create 1 admin if none exists
        if not User.objects.filter(is_superuser=True).exists():
            admin = AdminFactory(
                email='admin@example.com',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created admin user: {admin.email}')

        # Create workers and clients
        workers_count = int(count * 0.7)  # 70% workers
        clients_count = count - workers_count  # 30% clients

        workers = WorkerFactory.create_batch(workers_count)
        clients = ClientFactory.create_batch(clients_count)

        self.stdout.write(
            self.style.SUCCESS(f'Created {workers_count} workers and {clients_count} clients')
        )

    def seed_skills(self, count):
        self.stdout.write(f'Creating {count} skills...')
        
        # Predefined skills for better realism
        predefined_skills = [
            'Python Programming', 'JavaScript', 'React', 'Django', 'Node.js',
            'Data Analysis', 'Machine Learning', 'SQL', 'HTML/CSS', 'Project Management',
            'Digital Marketing', 'Graphic Design', 'Content Writing', 'SEO',
            'Customer Service', 'Sales', 'Accounting', 'Legal Research',
            'Translation', 'Video Editing'
        ]
        
        created_count = 0
        for skill_name in predefined_skills[:count]:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            if created:
                created_count += 1

        # Create additional random skills if needed
        remaining = count - created_count
        if remaining > 0:
            SkillFactory.create_batch(remaining)
            created_count += remaining

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} skills')
        )

    def seed_services(self, count):
        self.stdout.write(f'Creating {count} services...')
        
        # Ensure we have skills to associate
        if not Skill.objects.exists():
            self.seed_skills(20)

        services = ServiceFactory.create_batch(count)
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(services)} services')
        )

    def seed_locations(self, count):
        self.stdout.write(f'Creating {count} locations...')
        
        locations = LocationFactory.create_batch(count)
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(locations)} locations')
        )

    def seed_jobs(self, count):
        self.stdout.write(f'Creating {count} jobs...')
        
        # Ensure we have clients and skills
        if not User.objects.filter(role=User.Role.CLIENT).exists():
            ClientFactory.create_batch(10)
        
        if not Skill.objects.exists():
            self.seed_skills(20)

        if not Location.objects.exists():
            self.seed_locations(10)

        jobs = JobFactory.create_batch(count)
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(jobs)} jobs')
        )

    def seed_applications(self, count):
        self.stdout.write(f'Creating {count} job applications...')
        
        # Ensure we have workers and jobs
        if not User.objects.filter(role=User.Role.WORKER).exists():
            WorkerFactory.create_batch(20)
        
        if not Job.objects.exists():
            self.seed_jobs(30)

        applications = JobApplicationFactory.create_batch(count)
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(applications)} job applications')
        )
