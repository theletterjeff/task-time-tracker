class StartDateError(Exception):
    """
    Exception to raise when the start date of a model
    object is after the end or completed date
    """
    def __init__(self,
                 start_date,
                 second_date_var_name,
                 second_date):
        self.start_date = start_date
        self.second_date_var_name = second_date_var_name
        self.second_date = second_date
    
    def __str__(self):
        return (
            f'start_date ({self.start_date}) cannot come before '
            f'{self.second_date_var_name} ({self.second_date})'
        )