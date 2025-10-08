from django.shortcuts import render, redirect, get_object_or_404
from main.forms import ProductForm #ini import class dari forms.py
from main.models import Product #ini import class dari models.py
from django.http import HttpResponse
from django.core import serializers # untuk translate objek model menjadi format lain seperti xml atau json
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.contrib import messages
from django.shortcuts import redirect

import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required(login_url='/login')
def show_main(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'

    if filter_type == "all":
        product_list = Product.objects.all()
    else:
        product_list = Product.objects.filter(user=request.user)

    context = {
        'npm' : '2406437994',
        'name': request.user.username,
        'class': 'PBP B',
        'product_list': product_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, "main.html", context)

# Create your views here.
@login_required(login_url='/login')
def create_product(request):
    form = ProductForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        product_entry = form.save(commit = False)
        product_entry.user = request.user
        product_entry.save()
        messages.success(request, "Terimakasih telah menambah produk ^_^")  # <=== tambahkan ini    
        return redirect('main:show_main')

    context = {
        'form': form
    }

    return render(request, "create_product.html", context)

@login_required(login_url='/login')
def show_product(request, id):
    product = get_object_or_404(Product, pk=id)
    product.increment_views() # ini dari product_views dari models.py

    context = {
        'product': product
    }

    return render(request, "product_detail.html", context) # ini ntar ngirim ke product.detail html di direktori main/templates

def show_xml(request): # Mengembalikan data dalam bentuk xml
    product_list = Product.objects.all()
    xml_data = serializers.serialize("xml", product_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    product_list = Product.objects.all()
    data = [
        {
            'id': str(product.id),  # UUID harus diubah ke string
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'thumbnail': product.thumbnail,
            'category': product.category,
            'is_featured': product.is_featured,
            'product_views': product.product_views,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'user_id': product.user.id if product.user else None,  # pastikan user tidak null
        }
        for product in product_list
    ]
    return JsonResponse(data, safe=False)

def show_xml_by_id(request, product_id):
   try:
       product_item = Product.objects.filter(pk=product_id)
       xml_data = serializers.serialize("xml", product_item)
       return HttpResponse(xml_data, content_type="application/xml")
   except Product.DoesNotExist:
       return HttpResponse(status=404)
   
from django.http import JsonResponse
from .models import Product

def show_json_by_id(request, product_id):
    try:
        product = Product.objects.select_related('user').get(pk=product_id)
        data = {
            'id': str(product.id),
            'name': product.name,
            'description': product.description,
            'category': product.category,
            'thumbnail': product.thumbnail,
            'product_views': product.product_views,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'is_featured': product.is_featured,
            'user_id': product.user.id if product.user else None,
            'user_username': product.user.username if product.user else None,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)

   
def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Selamat datang di Toko Bola Hafiz ^_^")  # <=== tambahkan ini
            messages.success(request, 'Akun toko kamu sukses dibuat!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Selamat datang di Toko Bola Hafiz ^w^")  # <=== tambahkan ini
        response = HttpResponseRedirect(reverse("main:show_main"))
        response.set_cookie('last_login', str(datetime.datetime.now()))
        return response

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    messages.info(request, "Telah keluar dari akun")  # <=== tambahkan ini
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

def edit_product(request, id):
    product = get_object_or_404(Product, pk=id)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid() and request.method == 'POST':
        form.save()
        messages.info(request, "Ada update terbaru nihh!")  # <=== tambahkan ini
        return redirect('main:show_main')

    context = {
        'form': form
    }

    return render(request, "edit_product.html", context)

def delete_product(request, id):
    product = get_object_or_404(Product, pk=id)
    product.delete()
    messages.error(request, "Produk telah dihapus T_T")  # <=== tambahkan ini
    return HttpResponseRedirect(reverse('main:show_main'))

@csrf_exempt
@require_POST
def add_product_ajax(request):
    # Ambil data dari POST
    name = strip_tags(request.POST.get("name"))  # strip HTML tags
    price = request.POST.get("price")  # ambil price
    description = strip_tags(request.POST.get("description"))  # strip HTML tags
    category = request.POST.get("category")
    thumbnail = request.POST.get("thumbnail")
    is_featured = request.POST.get("is_featured") == 'on'
    user = request.user if request.user.is_authenticated else None

    # Validasi minimal
    if not name or not description or not category or not price:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # Konversi price ke integer
    try:
        price = int(price)
    except ValueError:
        return JsonResponse({"error": "Price must be a number"}, status=400)

    # Simpan Product
    new_product = Product(
        name=name,
        price=price,  # pastikan price disimpan
        description=description,
        category=category,
        thumbnail=thumbnail,
        is_featured=is_featured,
        user=user
    )
    new_product.save()

    # Kembalikan response JSON
    return JsonResponse({
        "id": str(new_product.id),
        "name": new_product.name,
        "price": new_product.price,
        "description": new_product.description,
        "category": new_product.category,
        "thumbnail": new_product.thumbnail,
        "is_featured": new_product.is_featured,
        "user_id": new_product.user.id if new_product.user else None,
        "created_at": new_product.created_at.isoformat() if new_product.created_at else None,
    }, status=201)