# Quick Reference: Database Seeding Commands

## Basic Seeding Commands

### Seed Everything (Default Amounts)
```bash
python manage.py seed
```

### Seed with Custom Amounts
```bash
python manage.py seed --users 50 --skills 20 --services 15 --jobs 30 --applications 100
```

### Clear Existing Data and Reseed
```bash
python manage.py seed --clear
```

## Targeted Seeding

### Users Only
```bash
# Create 20 users (14 workers, 6 clients)
python manage.py seed --model users --users 20
```

### Skills Only
```bash
# Create 15 skills
python manage.py seed --model skills --skills 15
```

### Services Only
```bash
# Create 10 services (will create required skills if none exist)
python manage.py seed --model services --services 10
```

### Jobs Only
```bash
# Create 25 jobs (will create required clients and skills if none exist)
python manage.py seed --model jobs --jobs 25
```

### Job Applications Only
```bash
# Create 50 applications (will create required jobs and workers if none exist)
python manage.py seed --model applications --applications 50
```

## Common Use Cases

### Development Setup
```bash
# Quick setup for development with minimal data
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

### Admin User
An admin user is automatically created with these credentials:
- Email: admin@example.com
- Password: testpass123

## Notes

- All users are created with the password: `testpass123`
- Workers get 2-4 random skills
- Services are associated with 2-4 skills
- Jobs require 1-3 skills
- Job applications have a 20% chance of being hired
- Users have a 70% chance of being verified

For more detailed information about the seeding system, refer to `SEEDING.md`.
