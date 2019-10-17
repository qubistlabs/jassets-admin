from typing import List

from django.db import models


class StaticDataModel(models.Model):
    """ Contract for model that operates with static data """

    @classmethod
    def get_data(cls, *args, **kwargs) -> List['StaticDataModel']:
        raise NotImplementedError

    @classmethod
    def save_data(cls, *instances: 'StaticDataModel'):
        raise NotImplementedError

    class Meta:
        abstract = True


class StaticDataQuerySet(models.QuerySet):
    """
    QuerySet that's not work with DB
    and stores set of data given by model's get_data method
    """
    model: StaticDataModel

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = data

    def _get_result_cache(self):
        return self.data

    def _set_result_cache(self, value):
        self.data = value

    _result_cache = property(fget=_get_result_cache, fset=_set_result_cache)

    def _clone(self):
        return self

    def _filter_or_exclude(self, negate, *args, **kwargs):
        self._result_cache = self.model.get_data(*args, **kwargs)
        return self

    @property
    def ordered(self):
        return True

    def info_string(self):
        return f'QuerySet {id(self)}; {str(self._result_cache)}'

    def __repr__(self):
        return self.info_string()

    def __str__(self):
        return self.info_string()
