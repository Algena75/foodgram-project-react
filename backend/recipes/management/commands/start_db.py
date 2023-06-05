from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Preparing and executing migrations")
        call_command('makemigrations')
        call_command('migrate')
        print("Deleting contenttypes")
        ContentType.objects.all().delete()
        print("Loading data from fixtures.")
        call_command('loaddata', 'dump.json')
        call_command('collectstatic', '--no-input')
        print("Done")
