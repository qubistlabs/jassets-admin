import json

from datetime import datetime
from django.conf import settings
from loguru import logger
from urllib import request
from urllib.error import HTTPError
from uuid import uuid4

from ..models import Asset
from ..exceptions import ShowWarning, ShowMessage, ShowError

from .enums import TaskState
from .helpers import get_proxy
from .models import ValidationQueue, AssetHistory


ADD_TASK_URL = f'{settings.VALIDATOR_URL}/task/add'
GET_TASK_URL = f'{settings.VALIDATOR_URL}/task/get'
REMOVE_TASK_URL = f'{settings.VALIDATOR_URL}/task/remove'


class ValidationManager:

    @classmethod
    def validate(cls, validation_method, asset):
        task_id = str(uuid4())
        ValidationQueue.add(task_id, asset.uuid, validation_method)
        response_data = cls._send_to_validation(validation_method, asset, task_id)
        if response_data['state'] == TaskState.queued.value:
            raise ShowMessage(
                'Validation started'
            )
        else:
            raise ShowWarning(
                f'Validation can`t be done. Validator returned this: {response_data["result"]}'
            )

    @classmethod
    def process_results(cls):
        done_task_uuids = []
        for item in ValidationQueue.get_all():
            try:
                response_data = cls._ask_for_result(item.task_uuid)
            except HTTPError as e:
                logger.error(
                    f'Validation failed. Validator returned this: {e}')
                continue

            if response_data['state'] in (TaskState.queued.value, TaskState.running.value):
                continue

            if response_data['state'] == TaskState.failed.value:
                is_valid = False
                message = response_data["result"]
                logger.error(
                    f'Validation failed. Validator returned this: {response_data["result"]}')
            else:
                is_valid = response_data['result']
                message = ''
            done_task_uuids.append(item.task_uuid)
            cls._create_history_entry(item.asset_uuid, message, is_valid)
            Asset.set_active(item.asset_uuid, is_valid)
            logger.info(
                f'Asset {item.asset_uuid} is valid: {is_valid}')
        ValidationQueue.remove(done_task_uuids)

    @classmethod
    def _request(cls, url, data):
        payload = json.dumps(data)
        payload_bytes = payload.encode('utf-8')
        task_request = request.Request(url)
        task_request.add_header('Content-Type', 'application/json; charset=utf-8')
        task_request.add_header('Content-Length', len(payload_bytes))
        return request.urlopen(task_request, payload_bytes)

    @classmethod
    def _response_to_json(cls, response):
        string = response.read().decode('utf-8')
        return json.loads(string)

    @classmethod
    def _send_to_validation(cls, validation_method, asset, task_id):
        cls._check_settings()
        proxy = get_proxy(validation_method)(asset)
        data = {
            'args': proxy.get_data(),
            'id': task_id,
            'type': validation_method.value
        }
        response = cls._request(ADD_TASK_URL, data)
        return cls._response_to_json(response)

    @classmethod
    def _ask_for_result(cls, task_uuid):
        cls._check_settings()
        data = {
            'id': str(task_uuid),
        }
        response = cls._request(GET_TASK_URL, data)
        return cls._response_to_json(response)

    @classmethod
    def _create_history_entry(cls, uuid: str, message: str, is_valid: bool):
        ah = AssetHistory.from_asset(uuid)
        if ah is None:
            logger.error(f'Asset with UUID={uuid} not found')
        else:
            ah.result_message = message
            ah.is_valid = is_valid
            ah.validation_time = datetime.now()
            ah.save()

    @classmethod
    def _check_settings(cls):
        if settings.VALIDATOR_URL is None:
            raise ShowError('Validation service URL not set')
