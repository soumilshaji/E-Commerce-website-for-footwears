from django.contrib.auth.models import User,Group
from employee.models import Register,Cart,CartItem,Order,OrderItem
from .models import *
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,get_user_model
from manager.models import Product,Category
import datetime
from django.conf import settings
import stripe

from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse

# Create your views here.
#employee home page
stripe.api_key=settings.STRIPE_SECRET_KEY
def home(request):
    return render(request,'common/firstpage.html')

def form(request):
    if request.method == 'POST':
        PROFILE = request.FILES.get('profile')
        FRISTNAME=request.POST['first_name']
        LASTNAME=request.POST['last_name']
        USERNAME=request.POST['username']
        EMAIL=request.POST['email']
        password=request.POST['password']
        ADDRESS=request.POST['address']
        CITY=request.POST['city']
        STATE=request.POST['state']
        PHONE=request.POST['phone']
        POSTAL_CODE=request.POST['postal_code']

        if User.objects.filter(username=USERNAME).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'common/register.html')
        if User.objects.filter(email=EMAIL).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'common/register.html')

        u = User.objects.create_user(first_name=FRISTNAME, last_name=LASTNAME, username=USERNAME, password=password, email=EMAIL)
        u.save()
        customer = Register.objects.create(user=u, address=ADDRESS, phonenumber=PHONE, postal_code=POSTAL_CODE, state=STATE, profilephoto=PROFILE, city=CITY)
        customer.save()
        customer_obj, created = Group.objects.get_or_create(name='CUSTOMER')
        customer_obj.user_set.add(u)

        # Auto-login the new user and redirect to the shop
        login(request, u)
        messages.success(request, f'Welcome, {u.first_name}! Your account has been created.')
        return redirect('userhome')

    return render(request, 'common/register.html')

def login_user(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='CUSTOMER').exists():
            return redirect('userhome')
        else:
            return redirect('adminhome')
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            if user.groups.filter(name='CUSTOMER').exists():
                login(request, user)
                return redirect('userhome')
            else:
                # Manager login: ensure is_staff is set, then log in
                if not user.is_staff:
                    user.is_staff = True
                    user.save()
                login(request, user)
                return redirect('adminhome')
        else:
            messages.error(request,'Invalid username or passsword')
            
    return render(request, 'common/login.html')


from django.core.paginator import Paginator
from django.db.models import Q

def userhome(request):
    # Exclude specifically the Yonex Power Cushion and all premium products
    data = Product.objects.filter(category__is_premium=False).exclude(name__icontains="Yonex Power Cushion 220")
    c = Category.objects.filter(is_premium=False)
    
    search = request.GET.get('search')
    category_param = request.GET.get('category')
    
    if search:
        data = data.filter(name__icontains=search)
    if category_param:
        if category_param.isdigit():
            data = data.filter(category_id=category_param)
        else:
            data = data.filter(category__name__icontains=category_param)
            
    # Use stable ordering for pagination consistency (newest first)
    data = data.order_by('-id')

    # Pagination: 15 products per page (5 columns × 3 rows)
    paginator = Paginator(data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.user.is_authenticated:
        w = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        w = []
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'user/product_grid.html', {
            'page_obj': page_obj, 
            'w': w,
            'search': search,
            'category_param': category_param
        })
        
    return render(request, 'user/userhome.html', {
        'page_obj': page_obj, 
        'c': c, 
        'w': w,
        'search': search,
        'category_param': category_param
    })

def special_category_view(request):
    data = Product.objects.filter(category__is_premium=True)
    c = Category.objects.filter(is_premium=True) # For search/filter dropdown
    
    search = request.GET.get('search')
    if search:
        if ',' in search:
            terms = search.split(',')
            query = Q()
            for term in terms:
                term = term.strip()
                query |= Q(name__icontains=term) | Q(category__name__icontains=term)
            data = data.filter(query)
        else:
            data = data.filter(Q(name__icontains=search) | Q(category__name__icontains=search))
    
    sort = request.GET.get('sort')
    if sort == 'price_low':
        data = data.order_by('price')
    elif sort == 'price_high':
        data = data.order_by('-price')
    elif sort == 'oldest':
        data = data.order_by('id')
    else:
        # Default: newest first
        data = data.order_by('-id')

    paginator = Paginator(data, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.user.is_authenticated:
        w = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        w = []
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'user/product_grid.html', {
            'page_obj': page_obj, 
            'w': w,
            'search': search,
            'special_view': True
        })
        
    return render(request, 'user/special_category.html', {
        'page_obj': page_obj, 
        'c': c, 
        'w': w,
        'search': search,
    })

# ///////////////////////////////////////////////////////////////////////////////////



def productdetails(request, id):
    product = get_object_or_404(Product, id=id)
    r = review.objects.filter(product=product)
    # Fetch 4 related products from the same category, excluding current product
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:4]
    return render(request, 'user/productdetails.html', {
        'product': product,
        'r': r,
        'related_products': related_products
    })



def addtocart(request,id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'login_required'}, status=401)
        messages.warning(request, "Please login to add items to cart")
        return redirect('login_user')

    if request.method == 'POST':
        product=get_object_or_404(Product,id=id)
        quantity=int(request.POST.get('quantity', 1))
        size=request.POST.get('size', '').strip()

        cart, created = Cart.objects.get_or_create(user=request.user)

        # Different sizes are treated as separate cart items
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity <= product.stock:
                cart_item.quantity = new_quantity
            else:
                cart_item.quantity = product.stock
            cart_item.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'product_name': product.name})

    return redirect('cartitems')


def buy_now(request, id):
    """Add product to cart and go directly to checkout."""
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to purchase.")
        return redirect('login_user')

    if request.method == 'POST':
        product = get_object_or_404(Product, id=id)
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '').strip()

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        if not created:
            new_quantity = cart_item.quantity + quantity
            cart_item.quantity = min(new_quantity, product.stock)
            cart_item.save()

    return redirect('checkout')


        
def cartitems(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = CartItem.objects.filter(cart=cart)

    grand_total = 0

    for item in items:
        item.total = item.product.price * item.quantity
        grand_total += item.total

    return render(request,'user/cart.html',{
        'items': items,
        'grand_total': grand_total
    })



def increase_quantity(request,id):
    item=get_object_or_404(CartItem,id=id)
    if item.quantity<item.product.stock:
        item.quantity+=1
        item.save()
    else:
        messages.error(request,'Out of stock')
    return redirect('cartitems')

def decrease_quantity(request,id):
    item= get_object_or_404(CartItem,id=id)
    if item.quantity<item.product.stock:
        item.quantity-=1
        item.save()
    if item.quantity == 0:
        item.delete()
    return redirect('cartitems')

def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    
    grand_total = 0
    
    for item in items:
        item.total = item.product.price * item.quantity
        grand_total += item.total
        
    return render(request,'user/checkout.html',{'items':items,'grand_total':grand_total})

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////// 

def cash_on_delivery(request):
    cart=Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cartitems')
    cart_items=CartItem.objects.filter(cart=cart)
    total=0
    for item in cart_items:
        total += item.product.price*item.quantity
    order=Order.objects.create(
        user=request.user,
        orderdate=datetime.datetime.now(),
        payment_method='COD',
        total_amount=total
    )
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity,
            size=item.size
        )
        item.product.stock -=item.quantity
        item.product.save()
    cart_items.delete()
    return redirect('ordersuccess',order.id)

def ordersuccess(request,id):
    o=get_object_or_404(Order,id=id)
    return render(request,'user/ordersuccess.html',{'order':o})

def vieworder(request):
    orders = OrderItem.objects.filter(order__user=request.user).order_by('-order__id')
    
    for item in orders:
        item.total = item.product.price * item.quantity
    return render(request,'user/vieworder.html',{'orders':orders})

def clear_order_history(request):
    if request.method == 'POST' and request.user.is_authenticated:
        # Delete all orders for this user (OrderItems cascade automatically)
        Order.objects.filter(user=request.user).delete()
        messages.success(request, 'Your order history has been cleared.')
    return redirect('vieworder')

    
def orderdetails(request,id):
    order = get_object_or_404(Order, id=id)
    items = OrderItem.objects.filter(order=order)
    
    if request.method == 'POST' and 'cancel_order' in request.POST:
        if order.orderstatus.lower() not in ['completed', 'canceled']:
            order.orderstatus = 'canceled'
            order.paymentstatus = 'Failed'
            order.cancel_reason = request.POST.get('cancel_reason', '')
            order.save()
            messages.warning(request, f'Order #{order.id:06d} has been cancelled.')
        return redirect('vieworder')
    
    return render(request,'user/orderdetails.html',{'order':order,'items':items})

def userdetails(request):
    user_details = Register.objects.get(user=request.user)    
    return render(request,'user/userdetails.html',{'user_details':user_details})

def edituser(request):
    user_details=Register.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get('profilephoto'):
            user_details.profilephoto = request.FILES['profilephoto']
        user_details.user.first_name = request.POST.get('first_name')
        user_details.user.last_name = request.POST.get('last_name')
        user_details.user.username = request.POST.get('username')
        user_details.user.email = request.POST.get('email')
        user_details.phonenumber = request.POST['phone']
        user_details.city = request.POST.get('city')
        user_details.state = request.POST.get('state')
        user_details.postal_code = request.POST.get('postal_code')
        user_details.save() 
        user_details.user.save()
        return redirect('userdetails')
    return render(request,'user/edituser.html',{'user_details':user_details})
    
    
def upi(request):
    cart=Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cartitems')
    cart_items=CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return redirect('cartitems')
    line_items=[]
    for item in cart_items:
            line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': item.product.name,
                },
              'unit_amount': int(item.product.price * 100),
            },
            'quantity':item.quantity,
        })
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:8000/payment_success',
        cancel_url='http://127.0.0.1:8000/cartitems',
    )
    
    return redirect(session.url)
    
def payment_success(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cartitems')
    cart_items=CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return redirect('cartitems')
    total=0
    for item in cart_items:
        total += item.product.price*item.quantity
    order=Order.objects.create(
        user=request.user,
        orderdate=datetime.datetime.now(),
        paymentstatus='paid',
        payment_method='UPI',
        total_amount=total,
    )
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity,
            size=item.size
        )
        item.product.stock -= item.quantity
        item.product.save()
    cart_items.delete()
    return redirect('ordersuccess',order.id)

def logout(request):
        if request.user.is_authenticated:
            request.session.flush()
        return redirect('home')


def generate_token():
     return get_random_string(20)

def password_reset_request(request):
    if request.method == "POST":
         email = request.POST.get('email')
         try:
             user = User.objects.get(email=email)
         except User.DoesNotExist:
             messages.error(request, "User with this email does not exist.")
             return redirect('password_reset_request')

         token =default_token_generator.make_token(user)
         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
         reset_url = request.build_absolute_uri(reverse('password_reset_confirm',kwargs={'uidb64':uidb64,'token':token}))
         subject = "Password Reset Request"
         message = render_to_string('common/password_reset_email.html', {
             'user': user,
             'reset_url': reset_url,
         })
         send_mail(subject, message,settings.DEFAULT_FROM_EMAIL, [user.email])
         messages.success(request, "A password reset link has been sent to your email.")
         return render(request,'common/emailsend.html')
    return render(request,'common/password_reset_form.html')

def password_reset_confirm(request, uidb64, token):
        User=get_user_model()
        try:
          uid = force_str(urlsafe_base64_decode(uidb64))
          user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            print(user)
        if user is not None and default_token_generator.check_token(user,token):
             if request.method == 'POST':
                  password1=request.POST.get('password1')
                  password2=request.POST.get('password2')

                  if password1 == password2:
                      user.password = make_password(password1)
                      user.save()
                      messages.success(request,'your password has been reset')
                      return render(request,'common/password_reset_confirm.html')
                  else:
                      messages.error(request,'password do not match')
                      return render(request,'common/password_reset_form.html')
                          
             return render(request,'common/password_reset_confirm.html')
        else:
           return render(request,'common/password_reset_form.html')
       
       
       
from django.http import JsonResponse

def add_to_wishlist(request,id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required'}, status=401)
        
    product=Product.objects.get(id=id)
    wishlist_item=Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()
    
    if wishlist_item:
        wishlist_item.delete()
        added = False
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )
        added = True
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'added': added})
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlistview'))


def wishlistview(request):
    wishlist_item=Wishlist.objects.filter(user=request.user)
    return render(request,'user/wishlist.html',{'w':wishlist_item})




def add_review(request,id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please login to share your review")
        return redirect('login_user')

    if request.method == "POST":
        comment=request.POST.get('comment')
        rating=request.POST.get('rating')
        
        product=Product.objects.get(id=id)
        
        review.objects.create(
            user=request.user,
            product=product,
            comment=comment,
            rating=rating
        )
    return redirect('productdetails',id=id)

def custom_404(request, exception):
    return render(request, '404.html', status=404)