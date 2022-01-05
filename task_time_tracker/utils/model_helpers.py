from datetime import timedelta
import pdb

from django.db.models import F, Q, Sum

import numpy as np

def get_col_sum(queryset, col_name: str) -> int:
    """Aggregate a column from a queryset,
    returning the value as an integer"""
    value = queryset.aggregate(Sum(col_name))[f'{col_name}__sum']
    if value is None or value == np.nan:
        value = 0
    return int(value)

def _convert_minutes_to_td(minutes: int) -> timedelta:
    """Take an integer or float of minutes, turn it into a timedelta object"""
    if minutes == None or minutes == np.nan:
        minutes = 0
    elif isinstance(minutes, np.int32):
        minutes = int(minutes)
    return timedelta(minutes=minutes)

def format_time(minutes: timedelta) -> str:
    """Take a timedelta object and return it formatted as a string"""
    if not isinstance(minutes, timedelta):
        minutes = _convert_minutes_to_td(minutes)

    seconds = int(minutes.total_seconds())

    if seconds == 0:
        total_time = '0 mins'
    
    else:
        periods = {
            'day': 60*60*24,
            'hr': 60*60,
            'min': 60,
        }

        strings=[]
        for period_name, period_seconds in periods.items():
            if seconds >= period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                if period_value == 1:
                    strings.append(f'{period_value} {period_name}')
                else:
                    strings.append(f'{period_value} {period_name}s')

        total_time = " ".join(strings)
    
    return total_time

class DashboardSummStats(object):

    def __init__(self, task_queryset):
        self.task_queryset = task_queryset

    @property
    def initial_estimated_time(self):
        return get_col_sum(self.task_queryset, 'expected_mins')
    
    @property
    def actual_time(self):
        return get_col_sum(self.task_queryset, 'actual_mins')
    
    @property
    def _estimated_no_actual_time(self):
        records_no_actual = self.task_queryset.filter(actual_mins=None)
        return get_col_sum(records_no_actual, 'expected_mins')
    
    @property
    def current_estimated_time(self):
        estimated_no_actual = self.task_queryset.filter(actual_mins=None)
        estimated_gt_actual = self.task_queryset.filter(expected_mins__gt=F('actual_mins'))
        estimated_lt_actual = self.task_queryset.filter(expected_mins__lt=F('actual_mins'))
        return (
            get_col_sum(estimated_no_actual, 'expected_mins') +
            get_col_sum(estimated_gt_actual, 'expected_mins') +
            get_col_sum(estimated_lt_actual, 'actual_mins')
        )
    
    @property
    def unfinished_time(self):
        records_unfinished = self.task_queryset.filter(completed=False)
        records_unfinished_wo_actual = records_unfinished.filter(actual_mins=None)
        records_unfinished_w_actual = records_unfinished.filter(~Q(actual_mins=None))


        records_unfinished_w_actual = self.task_queryset.annotate(
            expected_v_actual = F('expected_mins') - F('actual_mins')
        )
        records_time_remaining = records_unfinished_w_actual.filter(
            expected_v_actual__gt=0).filter(
                completed=False)

        return (
                get_col_sum(records_unfinished_wo_actual, 'expected_mins') +
                get_col_sum(records_time_remaining, 'expected_v_actual')
        )