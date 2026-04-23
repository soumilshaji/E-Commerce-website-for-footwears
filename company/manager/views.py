from django.shortcuts import render, redirect,get_object_or_404
from .models import Category,Product
from django.contrib import messages
from employee.models import Order,OrderItem,Register
from django.urls import reverse
import datetime


# Create your views here.

#manager home page
def adminhome(request):
    return render(request, 'manager/adminhome.html')

#add category
def category(request):
    is_special = request.GET.get('special') == 'true'
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        
        category=Category.objects.create(name=name, description=description, is_premium=is_special)
        category.save()
        
        messages.success(request,'CATEGORY ADDED SUCCESSFULL')
        
    return render(request, 'manager/category.html', {'is_special': is_special})

#category list
def view(request):
    is_special = request.GET.get('special') == 'true'
    if is_special:
        v = Category.objects.filter(is_premium=True)
    else:
        v = Category.objects.filter(is_premium=False)
    return render(request, 'manager/viewcate.html', {'data': v, 'is_special': is_special})

# DELETE category
def delete(request, id):
    category = get_object_or_404(Category, id=id)
    is_premium = category.is_premium
    category.delete()
    messages.success(request,'DELETED SUCCCESSFULL')
    url = reverse('view')
    if is_premium:
        url += "?special=true"
    return redirect(url)

# EDIT category
def editdata(request, id):
    s = get_object_or_404(Category, id=id)
    is_premium = s.is_premium
    if request.method == 'POST':
        s.name = request.POST['name']
        s.description = request.POST['description']
        s.save()
        messages.success(request, 'UPDATED SUCCESSFULLY')
        url = reverse('view')
        if is_premium:
            url += "?special=true"
        return redirect(url)
    r=Category.objects.filter(id=id)
    return render(request, 'manager/edit.html', {'s': s})


#add product
def add_product(request):
    is_special = request.GET.get('special') == 'true'
    if is_special:
        c = Category.objects.filter(is_premium=True)
    else:
        c = Category.objects.filter(is_premium=False)

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price'].replace(',', '')
        stock = request.POST['stock']
        image = request.FILES.get('image')
        category = request.POST['category']
        
        product=Product.objects.create(name=name, description=description, price=price, stock=stock, image=image, category_id=category)
        product.save()
        messages.success(request, 'PRODUCT ADDED SUCCESSFULLY')
        url = reverse('add_product')
        if is_special:
            url += "?special=true"
        return redirect(url)
    return render(request, 'manager/product.html', {'c': c, 'is_special': is_special})

#product list
def view_product(request):
    is_special = request.GET.get('special') == 'true'
    if is_special:
        viewproducts = Product.objects.filter(category__is_premium=True)
    else:
        viewproducts = Product.objects.filter(category__is_premium=False)
        
    total_count = viewproducts.count()
    low_stock_count = viewproducts.filter(stock__lt=3).count()
    
    # Calculate total value of catalog (sum of price * stock)
    total_value = sum((p.price or 0) * (p.stock or 0) for p in viewproducts)
    
    context = {
        'data': viewproducts,
        'total_count': total_count,
        'low_stock_count': low_stock_count,
        'total_value': f"{total_value:,.2f}",
        'is_special': is_special
    }
    return render(request, 'manager/view_product.html', context)

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# DELETE product
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    is_premium = product.category.is_premium if product.category else False
    product.delete()
    messages.success(request,'DELETED SUCCESSFULL')
    url = reverse('view_product')
    if is_premium:
        url += "?special=true"
    return redirect(url)

# EDIT product
def edit_product(request, id):
    c=Category.objects.all()
    s = get_object_or_404(Product, id=id)
    is_premium = s.category.is_premium if s.category else False
    if request.method == 'POST':
        s.name = request.POST.get('name')
        s.description = request.POST.get('description')
        s.price = request.POST.get('price', '').replace(',', '')
        s.stock = request.POST.get('stock')
        s.category_id = request.POST.get('category')
        if 'image' in request.FILES:
            s.image = request.FILES.get('image')
        s.save()
        messages.success(request, f'Product "{s.name}" updated successfully.')
        url = reverse('view_product')
        if is_premium:
            url += "?special=true"
        return redirect(url)
    editproduct=Product.objects.filter(id=id)
    return render(request, 'manager/editproduct.html', {'pdata': editproduct,'c':c})

# /////////////////////////////////////////////////////////////////////////////////////////

def canceled_order(request,id):
    order=get_object_or_404(Order,id=id)
    order.orderstatus='canceled'
    order.paymentstatus='failed'
    order.save()
    return redirect('userorder_for_admin')

def completeorder(request,id):
    order=get_object_or_404(Order,id=id)
    order.orderstatus='Completed'
    order.paymentstatus='Completed'
    order.save()
    return redirect('userorder_for_admin')


def userorder_for_admin(request):
    status=request.GET.get('status')
    orders=Order.objects.all()
    if status == 'pending':
        orders=Order.objects.filter(orderstatus__iexact='pending')
    if status == 'Processing':
        orders=Order.objects.filter(orderstatus__iexact='Processing')
    if status == 'Completed':
        orders=Order.objects.filter(orderstatus__iexact='Completed')
    if status == 'Canceled':
        orders=Order.objects.filter(orderstatus__in=['canceled', 'Canceled', 'cancelled', 'Cancelled'])
    if status == 'all':
        orders=Order.objects.all()
    return render(request,'manager/userorder.html',{'orders':orders})


def orderdetails_for_manager(request,id):
    order=get_object_or_404(Order,id=id)
    u=getattr(order.user,'register',None)
    if request.method == 'POST':
        if 'start_processing' in request.POST:
            order.orderstatus='Processing'
            order.trackingid=request.POST['TrackingID']
            order.deliverydate=request.POST['DELIVERY_DATE']
            order.carrier=request.POST['CARRIER']
            order.save()
            messages.success(request, f'Order #{order.id:06d} updated and marked as Processing.')
            return redirect('userorder_for_admin')
            
        if 'cancel_order' in request.POST:
            order.orderstatus='Canceled'
            order.paymentstatus='Failed'
            order.save()
            messages.warning(request, f'Order #{order.id:06d} has been Canceled.')
            return redirect('userorder_for_admin')
              
    return render(request,'manager/m_order_details.html',{
        'order':order,
        'u':u
    })


