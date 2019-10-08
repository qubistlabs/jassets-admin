from django.conf import settings
from django.core.management.base import BaseCommand
from time import sleep

from ...manager import ValidationManager


class Command(BaseCommand):
    help = 'Validation result receiver'

    def handle(self, *args, **options):
        while True:
            ValidationManager.process_results()
            sleep(settings.VALIDATION_TIMEOUT)
