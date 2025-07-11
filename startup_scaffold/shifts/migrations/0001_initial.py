# Generated by Django 5.2.3 on 2025-06-19 00:50

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_confirmed', models.BooleanField(default=False)),
                ('is_completed', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('missed', 'Missed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='scheduled', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('worker_feedback', models.TextField(blank=True)),
                ('geofence_lat', models.FloatField(blank=True, null=True)),
                ('geofence_lng', models.FloatField(blank=True, null=True)),
                ('geofence_radius_meters', models.FloatField(blank=True, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='jobs.job')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
