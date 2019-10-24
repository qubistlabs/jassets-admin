from abc import ABC, abstractmethod
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

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        result = True
        if exc_type is ShowWarning:
            messages.warning(self.request, exc_val)
        elif exc_type is ShowMessage:
            messages.info(self.request, exc_val)
        elif exc_type is ShowError:
            messages.error(self.request, exc_val)
        elif exc_type:
            result = False
        return result
