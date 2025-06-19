import factory
from django.utils import timezone
from datetime import timedelta
from jobs.models import Location, Job, JobApplication
from accounts.models import CustomUser
from services.models import Skill
from .accounts import UserFactory, ClientFactory, WorkerFactory
from .services import SkillFactory
from faker import Faker

fake = Faker()

class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location
        django_get_or_create = ('city', 'country')

    city = factory.LazyAttribute(lambda _: fake.city())
    state = factory.LazyAttribute(lambda _: fake.state())
    country = factory.LazyAttribute(lambda _: fake.country())

class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    client = factory.SubFactory(ClientFactory)
    title = factory.LazyAttribute(lambda _: fake.job())
    description = factory.LazyAttribute(lambda _: fake.text())
    location = factory.SubFactory(LocationFactory)
    budget = factory.LazyAttribute(lambda _: round(fake.random.uniform(50.0, 5000.0), 2))
    status = factory.Iterator([Job.Status.OPEN, Job.Status.IN_PROGRESS, Job.Status.COMPLETED])
    max_workers = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=5))
    expiry_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=fake.random_int(min=1, max=30)))
    created_at = factory.LazyFunction(lambda: fake.date_time_this_year())

    @factory.post_generation
    def required_skills(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for skill in extracted:
                self.required_skills.add(skill)
        else:
            # Add 1-3 random skills
            num_skills = fake.random_int(min=1, max=3)
            skills = SkillFactory.create_batch(num_skills)
            for skill in skills:
                self.required_skills.add(skill)

class JobApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobApplication

    job = factory.SubFactory(JobFactory)
    worker = factory.SubFactory(WorkerFactory)
    applied_at = factory.LazyFunction(lambda: fake.date_time_this_year())
    is_hired = factory.Faker('boolean', chance_of_getting_true=20)
