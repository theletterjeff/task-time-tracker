from django.test import TestCase

import pandas as pd

from .models import Task

class TaskModelTests(TestCase):
    
    def test_ordered_by_date_descending(self):
        """Model records are ordered by date descending"""
        created_dates = pd.Series(list(Task.objects.all().values('created_date')))
        diff_from_prior_date = created_dates.diff()
        date_gt_prior_date = diff_from_prior_date > 0
        self.assertIs(date_gt_prior_date, 1)