import lorem # Random words for testing
import numpy as np

from .models import Task

class UpdateActiveStatus(object):

    def __init__(self, get_response):
        self.get_response = get_response
        
        test_record = Task.objects.create(
            task_name=lorem.get_word(3),
            task_category=lorem.get_word(3),
            task_notes=lorem.get_word(25),
            expected_mins=np.random.randint(10,500),
        )
    
    def __call__(self, request):
        return self.get_response(request)