from django.shortcuts import render

# Create your views here.
# cores/views.py

from django.http import JsonResponse
from datetime import datetime

def server_time(request):
    return JsonResponse({'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
