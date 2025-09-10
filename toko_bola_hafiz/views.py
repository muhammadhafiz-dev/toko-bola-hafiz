from django.shortcuts import render

def home(request):
    context = {
        'npm': '12345678',
        'name': 'Hafiz',
        'class': 'PBP'
    }
    return render(request, 'index.html', context)
