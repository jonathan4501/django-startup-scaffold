import factory
from django.utils import timezone
from accounts.models import CustomUser
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.LazyAttribute(lambda _: fake.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    role = factory.Iterator([CustomUser.Role.WORKER, CustomUser.Role.CLIENT])
    is_active = True
    date_joined = factory.LazyFunction(timezone.now)
    phone_number = factory.LazyAttribute(lambda _: fake.numerify(text='##########'))  # 10 digits
    address = factory.LazyAttribute(lambda _: fake.address())
    is_verified = factory.Faker('boolean', chance_of_getting_true=70)
    last_seen = factory.LazyFunction(timezone.now)
    signup_ip = factory.LazyAttribute(lambda _: fake.ipv4())
    signup_device = factory.LazyAttribute(lambda _: fake.user_agent())
    average_rating = factory.LazyAttribute(lambda _: round(fake.random.uniform(1.0, 5.0), 2))
    rating_count = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=50))

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('testpass123')

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for skill in extracted:
                self.skills.add(skill)
        else:
            # Add 2-4 random skills for workers
            if self.role == CustomUser.Role.WORKER:
                from services.models import Skill
                num_skills = fake.random_int(min=2, max=4)
                available_skills = list(Skill.objects.all())
                if available_skills:  # Only add if there are skills available
                    selected_skills = fake.random_choices(available_skills, length=min(num_skills, len(available_skills)))
                    for skill in selected_skills:
                        self.skills.add(skill)

class AdminFactory(UserFactory):
    role = CustomUser.Role.ADMIN
    is_staff = True
    is_superuser = True

class WorkerFactory(UserFactory):
    role = CustomUser.Role.WORKER

class ClientFactory(UserFactory):
    role = CustomUser.Role.CLIENT
