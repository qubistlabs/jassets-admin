from abc import ABC, abstractmethod
from collections import Counter

from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from loguru import logger

from .exceptions import ShowMessage, ShowWarning, ShowError


class Speaker(ABC):
    """ Logging mechanism """

    @classmethod
    @abstractmethod
    def info(cls, msg):
        pass

    @classmethod
    @abstractmethod
    def warning(cls, msg):
        pass

    @classmethod
    @abstractmethod
    def error(cls, msg):
        pass


class LogSpeaker(Speaker):
    """ Emit log entries """

    @classmethod
    def info(cls, msg):
        logger.opt(depth=1).info(msg)

    @classmethod
    def warning(cls, msg):
        logger.opt(depth=1).warning(msg)

    @classmethod
    def error(cls, msg):
        logger.opt(depth=1).error(msg)


class ExceptionSpeaker(Speaker):
    """ Raise exceptions """

    @classmethod
    def info(cls, msg):
        raise ShowMessage(msg)

    @classmethod
    def warning(cls, msg):
        raise ShowWarning(msg)

    @classmethod
    def error(cls, msg):
        raise ShowError(msg)


class LogWrapper:
    """ Context manager that allow to catch exceptions and turn them to messages """
    request: WSGIRequest

    def __init__(self, request):
        self.request = request
        self._warning_list = []
        self._message_list = []
        self._error_list = []

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        result = True
        if exc_type is ShowWarning:
            self._warning_list.append(str(exc_val))
        elif exc_type is ShowMessage:
            self._message_list.append(str(exc_val))
        elif exc_type is ShowError:
            self._error_list.append(str(exc_val))
        elif exc_type:
            result = False
        return result

    def __del__(self):
        self._group_and_show(self._warning_list, messages.warning)
        self._group_and_show(self._message_list, messages.info)
        self._group_and_show(self._error_list, messages.error)

    def _group_and_show(self, collection, function):
        for msg, n in Counter(collection).items():
            if n == 1:
                text = msg
            else:
                text = f'{msg} [{n}]'
            function(self.request, text)
