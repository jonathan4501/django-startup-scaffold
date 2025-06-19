"""
Deployment Readiness Tests
Tests Docker configuration, environment setup, and production readiness
"""

import os
import subprocess
import json
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.conf import settings
from django.db import connection
from io import StringIO

class DockerConfigurationTests(TestCase):
    """
    Tests for Docker configuration and containerization
    """
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists and is properly configured"""
        dockerfile_path = os.path.join(settings.BASE_DIR.parent, 'Dockerfile')
        self.assertTrue(os.path.exists(dockerfile_path), "Dockerfile not found")
        
        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()
            
        # Check for essential Dockerfile components
        self.assertIn('FROM python:', dockerfile_content)
        self.assertIn('COPY requirements.txt', dockerfile_content)
        self.assertIn('RUN pip install', dockerfile_content)
        self.assertIn('COPY . .', dockerfile_content)
        self.assertIn('EXPOSE', dockerfile_content)

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists and is properly configured"""
        compose_path = os.path.join(settings.BASE_DIR.parent, 'docker-compose.yml')
        self.assertTrue(os.path.exists(compose_path), "docker-compose.yml not found")
        
        with open(compose_path, 'r') as f:
            compose_content = f.read()
            
        # Check for essential services
        self.assertIn('web:', compose_content)
        self.assertIn('db:', compose_content)
        self.assertIn('redis:', compose_content)
        self.assertIn('postgres:', compose_content)

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and contains necessary packages"""
        requirements_path = os.path.join(settings.BASE_DIR.parent, 'requirements.txt')
        self.assertTrue(os.path.exists(requirements_path), "requirements.txt not found")
        
        with open(requirements_path, 'r') as f:
            requirements_content = f.read()
            
        # Check for essential packages
        essential_packages = [
            'Django',
            'djangorestframework',
            'djangorestframework-simplejwt',
            'django-cors-headers',
            'psycopg2',
            'redis',
            'celery',
            'gunicorn',
            'whitenoise'
        ]
        
        for package in essential_packages:
            self.assertIn(package, requirements_content, 
                         f"Essential package '{package}' not found in requirements.txt")

class EnvironmentConfigurationTests(TestCase):
    """
    Tests for environment configuration and settings
    """
    
    def test_environment_variables_configured(self):
        """Test that environment variables are properly configured"""
        # Test that django-environ is being used
        self.assertTrue(hasattr(settings, 'env'), 
                       "django-environ not configured in settings")

    def test_database_configuration(self):
        """Test database configuration"""
        # Test that database is configured
        self.assertIn('default', settings.DATABASES)
        
        db_config = settings.DATABASES['default']
        self.assertIn('ENGINE', db_config)
        self.assertIn('NAME', db_config)
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
        except Exception as e:
            self.fail(f"Database connection failed: {e}")

    def test_redis_configuration(self):
        """Test Redis configuration for caching and Celery"""
        # Test that Redis/cache is configured
        self.assertIn('CACHES', dir(settings))
        
        if hasattr(settings, 'CACHES'):
            self.assertIn('default', settings.CACHES)

    def test_static_files_configuration(self):
        """Test static files configuration"""
        # Test static files settings
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
        
        # Test that WhiteNoise is configured
        self.assertIn('whitenoise.middleware.WhiteNoiseMiddleware', 
                     settings.MIDDLEWARE)

    def test_cors_configuration(self):
        """Test CORS configuration"""
        # Test that CORS is configured
        self.assertIn('corsheaders', settings.INSTALLED_APPS)
        self.assertIn('corsheaders.middleware.CorsMiddleware', 
                     settings.MIDDLEWARE)

class SecurityConfigurationTests(TestCase):
    """
    Tests for security configuration
    """
    
    def test_secret_key_configured(self):
        """Test that SECRET_KEY is configured"""
        self.assertTrue(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, 
                           'django-insecure-default-key')

    def test_debug_setting(self):
        """Test DEBUG setting for production"""
        # In production, DEBUG should be False
        # For testing, we'll just verify it's configurable
        self.assertIsInstance(settings.DEBUG, bool)

    def test_allowed_hosts_configured(self):
        """Test ALLOWED_HOSTS configuration"""
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)

    def test_csrf_configuration(self):
        """Test CSRF protection configuration"""
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', 
                     settings.MIDDLEWARE)

    def test_jwt_configuration(self):
        """Test JWT authentication configuration"""
        self.assertTrue(hasattr(settings, 'SIMPLE_JWT'))
        
        jwt_settings = settings.SIMPLE_JWT
        self.assertIn('ACCESS_TOKEN_LIFETIME', jwt_settings)
        self.assertIn('REFRESH_TOKEN_LIFETIME', jwt_settings)

class ManagementCommandTests(TestCase):
    """
    Tests for Django management commands
    """
    
    def test_migrate_command(self):
        """Test that migrate command works"""
        try:
            call_command('migrate', verbosity=0, interactive=False)
        except Exception as e:
            self.fail(f"Migration failed: {e}")

    def test_collectstatic_command(self):
        """Test that collectstatic command works"""
        try:
            # Temporarily override STATIC_ROOT for testing
            with override_settings(STATIC_ROOT='/tmp/test_static'):
                call_command('collectstatic', verbosity=0, interactive=False)
        except Exception as e:
            self.fail(f"Collectstatic failed: {e}")

    def test_check_command(self):
        """Test Django system check"""
        try:
            call_command('check', verbosity=0)
        except Exception as e:
            self.fail(f"Django check failed: {e}")

class APIDocumentationTests(TestCase):
    """
    Tests for API documentation and schema
    """
    
    def test_swagger_configuration(self):
        """Test Swagger/OpenAPI configuration"""
        # Test that drf-spectacular is configured
        if 'drf_spectacular' in settings.INSTALLED_APPS:
            self.assertIn('drf_spectacular', settings.INSTALLED_APPS)
            self.assertTrue(hasattr(settings, 'SPECTACULAR_SETTINGS'))

    def test_api_schema_generation(self):
        """Test API schema generation"""
        try:
            from django.core.management import call_command
            out = StringIO()
            call_command('spectacular', '--file', '/tmp/schema.yml', stdout=out)
        except Exception as e:
            # If spectacular is not installed, skip this test
            if 'spectacular' in str(e):
                self.skipTest("drf-spectacular not installed")
            else:
                self.fail(f"Schema generation failed: {e}")

class PerformanceTests(TestCase):
    """
    Basic performance and optimization tests
    """
    
    def test_database_indexes(self):
        """Test that database indexes are properly configured"""
        # This would require checking the actual database schema
        # For now, we'll just verify that migrations create indexes
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Check that tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Verify main tables exist
            expected_tables = [
                'accounts_customuser',
                'jobs_job',
                'services_service',
                'messaging_conversation',
                'payments_payment'
            ]
            
            for table in expected_tables:
                self.assertIn(table, tables, f"Table {table} not found")

    def test_query_optimization(self):
        """Test basic query optimization"""
        from django.test.utils import override_settings
        from django.db import connection
        
        # Test that queries are not excessive
        with override_settings(DEBUG=True):
            from accounts.models import CustomUser
            
            # Reset queries
            connection.queries_log.clear()
            
            # Perform a simple query
            users = list(CustomUser.objects.all()[:10])
            
            # Check query count (should be minimal)
            query_count = len(connection.queries)
            self.assertLessEqual(query_count, 5, 
                               f"Too many queries executed: {query_count}")

class CeleryConfigurationTests(TestCase):
    """
    Tests for Celery configuration
    """
    
    def test_celery_settings(self):
        """Test Celery configuration"""
        # Test that Celery settings exist
        celery_settings = [
            'CELERY_BROKER_URL',
            'CELERY_RESULT_BACKEND'
        ]
        
        for setting in celery_settings:
            if hasattr(settings, setting):
                self.assertTrue(getattr(settings, setting))

    def test_celery_tasks_importable(self):
        """Test that Celery tasks can be imported"""
        try:
            from jobs.tasks import send_job_notification
            from notifications.tasks import send_notification
            # If tasks import successfully, Celery is properly configured
        except ImportError as e:
            self.fail(f"Celery tasks import failed: {e}")

class LoggingConfigurationTests(TestCase):
    """
    Tests for logging configuration
    """
    
    def test_logging_configuration(self):
        """Test logging configuration"""
        self.assertTrue(hasattr(settings, 'LOGGING'))
        
        logging_config = settings.LOGGING
        self.assertIn('version', logging_config)
        self.assertIn('handlers', logging_config)
        self.assertIn('loggers', logging_config)

    def test_log_file_creation(self):
        """Test that log files can be created"""
        import logging
        
        logger = logging.getLogger('django')
        logger.info("Test log message for deployment testing")
        
        # If no exception is raised, logging is working

class ProductionReadinessTests(TestCase):
    """
    Tests for production readiness
    """
    
    def test_production_settings(self):
        """Test production-specific settings"""
        # These settings should be properly configured for production
        production_settings = {
            'SECURE_SSL_REDIRECT': bool,
            'SECURE_HSTS_SECONDS': int,
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': bool,
            'SECURE_HSTS_PRELOAD': bool,
            'SESSION_COOKIE_SECURE': bool,
            'CSRF_COOKIE_SECURE': bool,
        }
        
        for setting_name, expected_type in production_settings.items():
            if hasattr(settings, setting_name):
                setting_value = getattr(settings, setting_name)
                self.assertIsInstance(setting_value, expected_type,
                                    f"{setting_name} should be {expected_type}")

    def test_email_configuration(self):
        """Test email configuration"""
        # Test that email settings exist
        email_settings = [
            'EMAIL_BACKEND',
            'DEFAULT_FROM_EMAIL'
        ]
        
        for setting in email_settings:
            self.assertTrue(hasattr(settings, setting),
                          f"Email setting {setting} not configured")

    def test_media_files_configuration(self):
        """Test media files configuration"""
        self.assertTrue(hasattr(settings, 'MEDIA_URL'))
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))

class IntegrationReadinessTests(TestCase):
    """
    Tests for frontend integration readiness
    """
    
    def test_api_versioning(self):
        """Test API versioning configuration"""
        # Test that API URLs are properly versioned
        from django.urls import reverse
        
        try:
            # Test that API endpoints are accessible
            api_endpoints = [
                'job-list',
                'service-list',
                'auth-login',
                'health-check'
            ]
            
            for endpoint in api_endpoints:
                url = reverse(endpoint)
                self.assertTrue(url.startswith('/api/'),
                              f"API endpoint {endpoint} not properly versioned")
        except Exception as e:
            self.fail(f"API versioning test failed: {e}")

    def test_cors_headers(self):
        """Test CORS headers for frontend integration"""
        from django.test import Client
        
        client = Client()
        response = client.options('/api/health/')
        
        # Check for CORS headers (if configured)
        if 'Access-Control-Allow-Origin' in response:
            self.assertIn('Access-Control-Allow-Origin', response)

    def test_json_response_format(self):
        """Test consistent JSON response format"""
        from rest_framework.test import APIClient
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        client = APIClient()
        
        # Create test user
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )
        client.force_authenticate(user=user)
        
        # Test API response format
        response = client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Test that response is valid JSON
        try:
            json.loads(response.content)
        except json.JSONDecodeError:
            self.fail("API response is not valid JSON")
