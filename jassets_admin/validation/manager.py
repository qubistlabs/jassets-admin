import json

from typing import Any, Dict, Optional, Type
from django.conf import settings
from urllib import request
from urllib.error import HTTPError, URLError
from uuid import uuid4

from ..log_tools import LogSpeaker, Speaker

from .enums import TaskState, ValidationMethodEnum, ADAPTER_MAP
from .models import ValidationQueue


ADD_TASK_URL = f'{settings.VALIDATOR_URL}/task/add'
GET_TASK_URL = f'{settings.VALIDATOR_URL}/task/get'
REMOVE_TASK_URL = f'{settings.VALIDATOR_URL}/task/remove'


class ValidationManager:
    """ Higher API for validation procedures """
    def __init__(self):
        self._speaker = LogSpeaker

    def set_speaker(self, speaker: Type[Speaker]):
        """ Set logging mechanism """
        self._speaker = speaker

    def validate(self, validation_method, asset):
        """ Send asset to validation """
        task_id = str(uuid4())
        ValidationQueue.add(task_id, asset.uuid, validation_method)
        response_data = self._send_to_validation(validation_method, asset, task_id)
        if response_data:
            if response_data['state'] == TaskState.queued.value:
                self._speaker.info('Validation started')
            else:
                self._speaker.warning(
                    f'Validation can`t be done. Validator returned this: {response_data["result"]}'
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
                is_valid = False
                message = response_data["result"]
                self._speaker.error(
                    f'Validation failed. Validator returned this: {response_data["result"]}')
            else:
                is_valid = response_data['result']
                message = ''
            done_task_uuids.append(item.task_uuid)
            adapter = ADAPTER_MAP[ValidationMethodEnum(item.method)](asset_dict[item.asset_uuid])
            adapter.store_result(is_valid, message)
            self._speaker.info(
                f'Asset {item.asset_uuid} is valid: {is_valid}')
        ValidationQueue.remove(done_task_uuids)

    def clear_queue(self):
        """ Clear validation queue """
        ValidationQueue.remove_all()
        self._speaker.info('Validation queue cleared')

    def _request(self, url, data):
        """ Make request """
        payload = json.dumps(data)
        payload_bytes = payload.encode('utf-8')
        task_request = request.Request(url)
        task_request.add_header('Content-Type', 'application/json; charset=utf-8')
        task_request.add_header('Content-Length', len(payload_bytes))
        return request.urlopen(task_request, payload_bytes)

    def _response_to_dict(self, response) -> Dict[str, Any]:
        string = response.read().decode('utf-8')
        return json.loads(string)

    def _send_to_validation(self, validation_method, asset, task_id) -> Optional[Dict[str, Any]]:
        self._check_settings()
        adapter = ADAPTER_MAP[validation_method](asset)
        data = {
            'args': adapter.get_data(),
            'id': task_id,
            'type': validation_method.value
        }
        try:
            response = self._request(ADD_TASK_URL, data)
        except URLError:
            self._speaker.error('Validator service is unavailable')
        else:
            return self._response_to_dict(response)

    def _ask_for_result(self, task_uuid) -> Optional[Dict[str, Any]]:
        result = None
        self._check_settings()
        data = {
            'id': str(task_uuid),
        }
        try:
            response = self._request(GET_TASK_URL, data)
        except HTTPError as e:
            self._speaker.error(
                f'Validation failed. Validator returned this: {e}')
        except (URLError, ConnectionResetError):
            self._speaker.error(
                f'Validator service is unavailable')
        else:
            result = self._response_to_dict(response)
        return result

    def _check_settings(self):
        if settings.VALIDATOR_URL is None:
            self._speaker.error('Validation service URL not set')
