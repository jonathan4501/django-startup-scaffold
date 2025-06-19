import factory
from services.models import Skill, Service
from faker import Faker

fake = Faker()

class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill
        django_get_or_create = ('name',)

    name = factory.LazyAttribute(lambda _: fake.job())

class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    name = factory.LazyAttribute(lambda _: fake.catch_phrase())
    description = factory.LazyAttribute(lambda _: fake.text())
    is_active = True
    is_public = True
    created_at = factory.LazyFunction(lambda: fake.date_time_this_year())

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for skill in extracted:
                self.skills.add(skill)
        else:
            # Add 2-4 random skills
            num_skills = fake.random_int(min=2, max=4)
            skills = SkillFactory.create_batch(num_skills)
            for skill in skills:
                self.skills.add(skill)
