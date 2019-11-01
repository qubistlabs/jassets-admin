import requests

from django.conf import settings
from json import JSONDecodeError
from typing import Any, Dict, Optional, Type
from uuid import uuid4

from ..log_tools import LogSpeaker, Speaker

from .adapters import ADAPTER_MAP
from .enums import TaskState, ValidationMethodEnum
from .models import ValidationQueue


ADD_TASK_URL = f'http://{settings.VALIDATOR_HOST}:{settings.VALIDATOR_PORT}/task/add'
GET_TASK_URL = f'http://{settings.VALIDATOR_HOST}:{settings.VALIDATOR_PORT}/task/get'
REMOVE_TASK_URL = f'http://{settings.VALIDATOR_HOST}:{settings.VALIDATOR_PORT}/task/remove'


class ValidationManager:
    """ Higher API for validation procedures """
    def __init__(self):
        self._speaker = LogSpeaker

    def set_speaker(self, speaker: Type[Speaker]):
        """ Set logging mechanism """
        self._speaker = speaker

    def validate(self, validation_method, asset, *args, **kwargs):
        """ Send asset to validation """
        task_id = str(uuid4())
        ValidationQueue.add(task_id, asset.uuid, validation_method)
        response_data = self._send_to_validation(validation_method, asset, task_id, *args, **kwargs)
        if response_data:
            if response_data['state'] == TaskState.queued.value:
                self._speaker.info('Process started')
            else:
                self._speaker.warning(
                    f'Process can`t be done. Validator returned this: {response_data["result"]}'
                )

    def process_results(self):
        """ Process validation results for all assets in queue """
        done_task_uuids = []
        asset_dict = ValidationQueue.associated_assets_dict()
        for item in ValidationQueue.get_all():
            if item.asset_uuid not in asset_dict:
                self._speaker.error(f'Asset with UUID={item.asset_uuid} not found')
                continue
            response_data = self._ask_for_result(item.task_uuid)
            if response_data is None:
                continue

            if response_data['state'] in (TaskState.queued.value, TaskState.running.value):
                continue

            if response_data['state'] == TaskState.failed.value:
                result = None
                message = response_data["result"]
                self._speaker.error(
                    f'Validation failed. Validator returned this: {response_data["result"]}')
            else:
                result = response_data['result']
                message = ''
            done_task_uuids.append(item.task_uuid)
            adapter = ADAPTER_MAP[ValidationMethodEnum(item.method)](asset_dict[item.asset_uuid])
            adapter.store_result(result, message)
            self._speaker.info(
                f'Asset {item.asset_uuid} is valid: {result}')
        ValidationQueue.remove(done_task_uuids)

    def clear_queue(self):
        """ Clear validation queue """
        self._check_settings()
        for item in ValidationQueue.get_all():
            data = {'id': str(item.task_uuid)}
            self._request(REMOVE_TASK_URL, data)
        ValidationQueue.remove_all()
        self._speaker.info('Validation queue cleared')

    def _request(self, url, data):
        """ Make request """
        try:
            return requests.post(url=url, json=data).json()
        except requests.HTTPError as e:
            self._speaker.error(f'Error happened. Validator service returned this: {e}')
            return None
        except requests.ConnectionError:
            self._speaker.error('Validator service is unavailable')
            return None
        except JSONDecodeError:
            return None

    def _send_to_validation(
            self,
            validation_method,
            asset,
            task_id,
            *args,
            **kwargs
    ) -> Optional[Dict[str, Any]]:
        self._check_settings()
        adapter = ADAPTER_MAP[validation_method](asset, *args, **kwargs)
        data = {
            'args': adapter.get_data(),
            'id': task_id,
            'type': validation_method.value
        }
        return self._request(ADD_TASK_URL, data)

    def _ask_for_result(self, task_uuid) -> Optional[Dict[str, Any]]:
        self._check_settings()
        data = {
            'id': str(task_uuid),
        }

        return self._request(GET_TASK_URL, data)

    def _check_settings(self):
        if settings.VALIDATOR_HOST is None or settings.VALIDATOR_PORT is None:
            self._speaker.error('Validation service host and port must be set')
