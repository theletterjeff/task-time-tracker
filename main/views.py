from django.shortcuts import render

def index(request):
    """Home page"""
    template = 'main/index.html'
    return render(request, template)