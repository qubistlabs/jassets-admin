from django.core.management.base import BaseCommand

from ....log_tools import LogSpeaker

from ...manager import ValidationManager


class Command(BaseCommand):
    help = 'Validation result receiver'

    def handle(self, *args, **options):
        manager = ValidationManager()
        manager.set_speaker(LogSpeaker)
        manager.clear_queue()
