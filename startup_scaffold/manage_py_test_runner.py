import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def run_tests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'startup_scaffold.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['ratings', 'shifts', 'jobs'])
    sys.exit(bool(failures))

if __name__ == '__main__':
    run_tests()
