from django.core.management.base import BaseCommand
import csv
from .models import Partner

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **kwargs):
        with open(kwargs['file_path'], newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Partner.objects.create(**row)
                
# python manage.py import_data data.csv