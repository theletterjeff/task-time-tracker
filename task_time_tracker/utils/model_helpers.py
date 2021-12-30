from datetime import timedelta
import pdb

from django.db.models import Sum

def _convert_minutes_to_td(minutes) -> timedelta:
    """Take an integer or float of minutes, turn it into a timedelta object"""
    if minutes == None:
        minutes = 0
    return timedelta(minutes=minutes)

def format_time(minutes: timedelta) -> str:
    """Take a timedelta object and return it formatted as a string"""
    if not isinstance(minutes, timedelta):
        minutes = _convert_minutes_to_td(minutes)

    seconds = int(minutes.total_seconds())
    periods = {
        'yr': 60*60*24*365,
        'mth': 60*60*24*30,
        'day': 60*60*24,
        'hr': 60*60,
        'min': 60,
        'sec': 1,
    }

    strings=[]
    for period_name, period_seconds in periods.items():
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            if period_value == 1:
                strings.append(f'{period_value} {period_name}')
            else:
                strings.append(f'{period_value} {period_name}s')

    return " ".join(strings)

class DashboardSummStats(object):

    def __init__(self, task_queryset):
        # Pass in the active tasks queryset
        self.task_queryset = task_queryset

    @property
    def estimated_time(self):
        return self.task_queryset.aggregate(Sum('expected_mins'))['expected_mins__sum']
    
    @property
    def actual_time(self):
        return self.task_queryset.aggregate(Sum('actual_mins'))['actual_mins__sum']
    
    @property
    def estimated_no_actual_time(self):
        records_no_actual = self.task_queryset.filter(actual_mins=None)
        # pdb.set_trace()
        return records_no_actual.aggregate(Sum('expected_mins'))['expected_mins__sum']
    
    @property
    def estimated_plus_actual_time(self):
        try:
            estimated_plus_actual_time = self.actual_time + self.estimated_no_actual_time
        except TypeError:
            estimated_plus_actual_time = 0
        return estimated_plus_actual_time
    
    @property
    def unfinished_time(self):
        records_unfinished = self.task_queryset.filter(completed=False)
        records_unfinished_estimated_no_actual = records_unfinished.filter(actual_mins=None)

        try:
            unfinished_time = (
                records_unfinished.aggregate(Sum('actual_mins'))['actual_mins__sum']
                + records_unfinished_estimated_no_actual.aggregate(Sum('expected_mins'))['expected_mins__sum']
            )
        except TypeError:
            unfinished_time = 0
        return unfinished_time
        