from time import sleep
from datetime import datetime

from loguru import logger
from django.conf import settings
from django.core.management.base import BaseCommand

from ....log_tools import LogSpeaker
from ....models import Asset

from ...enums import ValidationMethodEnum
from ...manager import ValidationManager


def schedule_validation():
    """Schedule new validation tasks.

    Schedule update of supply and volume 24h fields based on last validation
    time.
    """
    manager = ValidationManager()

    for asset in Asset.objects.requires_validation()[:10]:
        asset.last_scheduled_validation = datetime.now()
        asset.save(update_fields=('last_scheduled_validation',))

        manager.validate(ValidationMethodEnum.ALL_SUPPLY_TYPES_GETTER, asset)
        manager.validate(ValidationMethodEnum.CMC_VOLUME24H_GETTER, asset)

        logger.info("Schedule %s validation", asset.symbol)


class Command(BaseCommand):
    help = 'Validation result receiver'

    def handle(self, *args, **options):
        manager = ValidationManager()
        manager.set_speaker(LogSpeaker)
        logger.info('Successfully started')
        while True:
            manager.process_results()

            # TODO: tmp solution, need a separate task
            schedule_validation()

            sleep(settings.VALIDATION_TIMEOUT)
