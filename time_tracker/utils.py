from datetime import timedelta

from django.shortcuts import redirect
from django.urls import reverse

import numpy as np

def view_form(form, request):
    if request.method == 'POST':
        form = form(data=request.POST)
    else:
        form = form()
    return form

def post_form_data(form, url_name='dashboard'):
    """Post form data to database"""
    if form.is_valid():
        form.save()
        reload_url = reverse(url_name)
        return redirect(reload_url)

### Functions for summary time stats ###

def _td_format(td_object: timedelta) -> str:
    """Take a timedelta object and return it formatted as a string"""
    seconds = int(td_object.total_seconds())
    periods = {
        'year': 60*60*24*365,
        'month': 60*60*24*30,
        'day': 60*60*24,
        'hour': 60*60,
        'minute': 60,
        'second': 1,
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

def _sum_format_times(times_list: list) -> str:
    """Take list of estimated times in minutes,
    return string of total estimated time in hrs/mins format"""
    total_time = np.sum(times_list)
    return _td_format(total_time)

def calc_estimated_time(estimated_times: list) -> str:
