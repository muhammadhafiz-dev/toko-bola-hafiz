from django.shortcuts import render

def show_main(request):
    context = {
        'npm' : '2406437994',
        'name': 'Muhammad Hafiz Hanan',
        'class': 'PBP A'
    }

    return render(request, "main.html", context)
# Create your views here.
