from django.shortcuts import render, redirect,get_object_or_404
from .models import Category,Product
from django.contrib import messages
from employee.models import Order,OrderItem,Register
import datetime


# Create your views here.

#manager home page
def adminhome(request):
    return render(request, 'manager/adminhome.html')

#add category
def category(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        
        category=Category.objects.create(name=name, description=description)
        category.save()
        
        messages.success(request,'CATEGORY ADDED SUCCESSFULL')
        
    return render(request, 'manager/category.html')

#category list
def view(request):
    v = Category.objects.all()
    return render(request, 'manager/viewcate.html', {'data': v})

# DELETE category
def delete(request, id):
    Category.objects.filter(id=id).delete()
    messages.success(request,'DELETED SUCCCESSFULL')
    return redirect('view')

# EDIT category
def editdata(request, id):
    s = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        s.name = request.POST['name']
        s.description = request.POST['description']
        s.save()
        messages.success(request, 'UPDATED SUCCESSFULLY')
        return redirect('view')
    r=Category.objects.filter(id=id)
    return render(request, 'manager/edit.html', {'s': s})


#add product
def add_product(request):
    c=Category.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price'].replace(',', '')
        stock = request.POST['stock']
        image = request.FILES.get('image')
        category = request.POST['category']
        
        product=Product.objects.create(name=name, description=description, price=price, stock=stock, image=image, category_id=category)
        product.save()
    return render(request, 'manager/product.html',{'c':c})

#product list
def view_product(request):
    viewproducts = Product.objects.all()
    return render(request, 'manager/view_product.html', {'data': viewproducts})

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# DELETE product
def delete_product(request, id):
    Product.objects.filter(id=id).delete()
    messages.success(request,'DELETED SUCCESSFULL')
    return redirect('view_product')

# EDIT product
def edit_product(request, id):
    c=Category.objects.all()
    s = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        s.name = request.POST['name']
        s.description = request.POST['description']
        s.price = request.POST['price']
        s.stock = request.POST['stock']
        s.category_id=request.POST['category']
        if 'image' in request.FILES:
            s.image = request.FILES['image']
        s.save()
    editproduct=Product.objects.filter(id=id)
    return render(request, 'manager/edit_product.html', {'pdata': editproduct,'c':c})

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
        orders=Order.objects.filter(orderstatus='pending')
    if status == 'Processing':
        orders=Order.objects.filter(orderstatus='Processing')
    if status == 'Completed':
        orders=Order.objects.filter(orderstatus='Completed')
    if status == 'Canceled':
        orders=Order.objects.filter(orderstatus='canceled')
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
        if 'cancel_order' in request.POST:
            order.orderstatus='Canceled'
            order.paymentstatus='Failed'
            order.save()
              
    return render(request,'manager/m_order_details.html',{
        'order':order,
        'u':u
    })


