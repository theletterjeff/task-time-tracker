from django.shortcuts import redirect
from django.urls import reverse

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