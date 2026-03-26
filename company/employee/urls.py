from django.urls import path
from employee import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home'),
    path('form',views.form,name='form'),    
    path('login_user/',views.login_user,name='login_user'),
    path('logout',views.logout,name='logout'),
    path('userhome', views.userhome, name='userhome'),
    path('productdetails/<int:id>/',views.productdetails,name='productdetails'),
    
    path('addtocart/<int:id>/',views.addtocart,name='addtocart'),
    path('cartitems/', views.cartitems, name='cartitems'),
    
    path('increase_quantity/<int:id>',views.increase_quantity,name='increase_quantity'),
    path('decrease_quantity/<int:id>/', views.decrease_quantity, name='decrease_quantity'),
    
    path('checkout',views.checkout,name='checkout'),
    path('cash_on_delivery',views.cash_on_delivery,name='cash_on_delivery'),
    
    path('ordersuccess/<int:id>',views.ordersuccess,name='ordersuccess'),
    path('vieworder',views.vieworder,name='vieworder'),
    path('orderdetails/<int:id>/',views.orderdetails,name='orderdetails'),
    path('userdetails',views.userdetails,name='userdetails'),
    path('edituser',views.edituser,name='edituser'),
    path('payment_success/',views.payment_success,name='payment_success'),
    path('upi',views.upi,name='upi'),
    path('password_reset_request/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('add_to_wishlist/<int:id>',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlistview/',views.wishlistview,name='wishlistview'),
    path('add_review/<int:id>',views.add_review,name='add_review')


]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)