import logging

from abc import ABC, abstractmethod
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

