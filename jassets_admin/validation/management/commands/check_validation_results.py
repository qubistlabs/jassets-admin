from django.conf import settings
from django.core.management.base import BaseCommand
from loguru import logger
from time import sleep

from ....log_tools import LogSpeaker

from ...manager import ValidationManager


class Command(BaseCommand):
    help = 'Validation result receiver'

    def handle(self, *args, **options):
        manager = ValidationManager()
        manager.set_speaker(LogSpeaker)
        logger.info('Successfully started')
        while True:
            manager.process_results()
            sleep(settings.VALIDATION_TIMEOUT)
