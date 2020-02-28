import requests

from django.conf import settings
from json import JSONDecodeError
from typing import Any, Dict, Optional, Type
from uuid import uuid4

from ..log_tools import LogSpeaker, Speaker

from jassets_admin.validation.adapters import ADAPTER_MAP
from jassets_admin.validation.enums import TaskState, ValidationMethodEnum, ValidatorErrors
from jassets_admin.validation.models import ValidationQueue, AssetHistory
from jassets_admin.models import Asset

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

    def validate(self, validation_method, asset, user=None, *args, **kwargs):
        """ Send asset to validation """
        task_id = str(uuid4())
        ValidationQueue.add(task_id, asset.uuid, validation_method)
        response_data = self._send_to_validation(
            validation_method, asset, task_id, user, *args, **kwargs,
        )
        if response_data:
            if response_data['state'] == TaskState.queued.value:
                self._speaker.info('Process started')
            else:
                self._speaker.warning(
                    f'Process can`t be done. Validator returned this: {response_data["result"]}'
                )

    def approval(self, history_entry, is_approved):
        """ Apply or discard asset changes after approval """
        if history_entry.state == AssetHistory.APPLIED:
            self._speaker.warning('Changes are already applied')
        elif history_entry.state == AssetHistory.DISCARDED:
            self._speaker.warning('Changes are already discarded')
        elif history_entry.state == AssetHistory.DRAFT:
            self._speaker.warning(
                f'Changes you want to {"apply" if is_approved else "discard"} are not arrived yet',
            )
        elif history_entry.state == AssetHistory.PENDING:
            adapter_cls = ADAPTER_MAP[ValidationMethodEnum(history_entry.validation_method)]
            if adapter_cls.need_approval is False:
                self._speaker.error('This validator does not imply result approval')
            try:
                asset = Asset.objects.get(uuid=history_entry.uuid)
            except Asset.DoesNotExist:
                self._speaker.error(f'Asset with uuid = {history_entry.uuid} not found')
            else:
                adapter = adapter_cls(asset)
                adapter.result_approval(history_entry, is_approved)
                self._speaker.info('Approved' if is_approved else 'Discarded')

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
            try:
                state = TaskState(response_data['state'])
            except ValueError:
                self._speaker.info(
                    f"Validator service returned result with unknown "
                    f"status: {response_data['state']}"
                )
            else:
                if state in (TaskState.queued, TaskState.running):
                    continue

                if state == TaskState.failed:
                    result = None
                    message = response_data["result"]
                    self._speaker.error(
                        f'Validation failed. Validator returned this: {response_data["result"]}')
                else:
                    result = response_data['result']
                    message = ''
                done_task_uuids.append(item.task_uuid)
                adapter = ADAPTER_MAP[ValidationMethodEnum(item.method)](asset_dict[item.asset_uuid])
                adapter.store_result(item.task_uuid, result, message, state)
                self._speaker.info(f'Asset {item.asset_uuid} result: {result}')
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
            response = requests.post(url=url, json=data)
            if response.status_code == requests.codes.ok:
                return response.json()
            else:
                response.raise_for_status()
        except requests.HTTPError as e:
            if not self._handle_http_error(e.response):
                self._speaker.error(f'Error happened. Validator service returned this: {e}')
        except requests.ConnectionError as e:
            self._speaker.error(f'Validator service is unavailable. {e}')
        except JSONDecodeError as e:
            self._speaker.error(f'Validator service returned unreadable answer. {e}')

    def _send_to_validation(
            self,
            validation_method,
            asset,
            task_id,
            user,
            *args,
            **kwargs
    ) -> Optional[Dict[str, Any]]:
        self._check_settings()
        adapter = ADAPTER_MAP[validation_method](asset, *args, **kwargs)
        adapter.create_history_entry(task_id, user)
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

    def _handle_http_error(self, response) -> bool:
        """
        Try to handle error returned from validator
        Returns True if error handled
        """
        key = (response.status_code, response.reason)
        try:
            enum_item = ValidatorErrors(key)
        except ValueError:
            return False
        if enum_item == ValidatorErrors.NO_TASK:
            task_uuid = response.text
            self._speaker.warning((
                f"Validator service responded that task with UUID = {task_uuid} not found. "
                f"Deleting task from queue."
            ))
            ValidationQueue.remove([task_uuid])
            return True
        return False
