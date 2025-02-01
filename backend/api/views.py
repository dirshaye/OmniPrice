from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    return render(request, 'index.html')

def get_data(request):
    data = {
        'message': 'Hello from Django!'
    }
    return JsonResponse(data)

# Create your views here.
