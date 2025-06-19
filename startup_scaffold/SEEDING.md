# Database Seeding Guide

This project includes a comprehensive seeding system to populate your database with realistic test data.

## Installation

The required packages are already included in requirements.txt:
- `django-seed`: For easy data generation
- `factory-boy`: For creating model factories
- `faker`: For generating fake data

## Usage

### Basic Seeding

To seed the database with default amounts of data:

```bash
python manage.py seed
```

This will create:
- 50 users (35 workers, 15 clients, 1 admin)
- 20 skills
- 15 services
- 10 locations
- 30 jobs
- 100 job applications

### Custom Amounts

You can specify the number of records to create for each model:

```bash
python manage.py seed --users 100 --jobs 50 --applications 200
```

### Seed Specific Models

To seed only specific models:

```bash
# Seed only users
python manage.py seed --model users --users 25

# Seed only jobs
python manage.py seed --model jobs --jobs 20

# Seed only skills
python manage.py seed --model skills --skills 30
```

Available models:
- `users`: Creates workers, clients, and admin users
- `skills`: Creates skill records
- `services`: Creates service records with associated skills
- `locations`: Creates location records
- `jobs`: Creates job postings with required skills and locations
- `applications`: Creates job applications from workers to jobs
- `all`: Seeds all models (default)

### Clear and Reseed

To clear existing data and start fresh:

```bash
python manage.py seed --clear
```

**Warning**: This will delete all existing data except superuser accounts!

## Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--users` | int | 50 | Number of users to create |
| `--skills` | int | 20 | Number of skills to create |
| `--services` | int | 15 | Number of services to create |
| `--locations` | int | 10 | Number of locations to create |
| `--jobs` | int | 30 | Number of jobs to create |
| `--applications` | int | 100 | Number of job applications to create |
| `--model` | str | all | Specific model to seed |
| `--clear` | flag | False | Clear existing data before seeding |

## Generated Data

### Users
- **Admin User**: `admin@example.com` (password: `testpass123`)
- **Workers**: Random users with worker role, skills, and profiles
- **Clients**: Random users with client role and profiles
- All users have realistic names, emails, phone numbers, and addresses

### Skills
Includes both predefined realistic skills and randomly generated ones:
- Programming: Python, JavaScript, React, Django, Node.js
- Data: Data Analysis, Machine Learning, SQL
- Design: Graphic Design, HTML/CSS, Video Editing
- Business: Project Management, Digital Marketing, Sales
- And more...

### Services
- Random service names and descriptions
- Associated with 2-4 relevant skills
- Mix of active/inactive and public/private services

### Jobs
- Realistic job titles and descriptions
- Associated with 1-3 required skills
- Random budgets between $50-$5000
- Various statuses (open, in progress, completed)
- Expiry dates within the next 30 days

### Job Applications
- Workers applying to relevant jobs
- 20% chance of being hired
- Realistic application timestamps

## Examples

### Development Setup
```bash
# Quick setup for development
python manage.py seed --users 20 --jobs 10 --applications 30
```

### Testing Setup
```bash
# Larger dataset for testing
python manage.py seed --users 100 --jobs 50 --applications 200
```

### Demo Setup
```bash
# Clean slate with demo data
python manage.py seed --clear --users 30 --jobs 15 --applications 50
```

### Specific Model Testing
```bash
# Test user creation only
python manage.py seed --model users --users 10

# Test job creation with dependencies
python manage.py seed --model jobs --jobs 5
```

## Factory Classes

The seeding system uses Factory Boy factories located in `core/management/commands/factories/`:

- `UserFactory`: Creates basic users
- `AdminFactory`: Creates admin users
- `WorkerFactory`: Creates worker users
- `ClientFactory`: Creates client users
- `SkillFactory`: Creates skills
- `ServiceFactory`: Creates services with skills
- `LocationFactory`: Creates locations
- `JobFactory`: Creates jobs with all dependencies
- `JobApplicationFactory`: Creates job applications

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all required models exist before seeding dependent models
2. **Unique Constraints**: The seeder handles unique constraints for skills and locations
3. **Foreign Key Errors**: Dependencies are automatically created if they don't exist

### Debug Mode

For verbose output, use Django's verbosity flag:

```bash
python manage.py seed --verbosity 2
```

## Extending the Seeder

To add new models to the seeding system:

1. Create a factory in the appropriate factory file
2. Add the model to the seed command
3. Update this documentation

Example factory:
```python
class MyModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MyModel
    
    name = factory.LazyAttribute(lambda _: fake.name())
    # Add other fields...
