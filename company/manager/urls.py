from django.urls import path
from manager import views


urlpatterns = [
    path('adminhome',views.adminhome,name='adminhome'),
    path('category',views.category,name='category'),
    path('view',views.view,name='view'), 
    
    path('delete/<int:id>',views.delete,name='delete'),
    path('editdata/<int:id>',views.editdata,name='editdata'),

    
    path('add_product',views.add_product,name='add_product'),
    path('view_product',views.view_product,name='view_product'),
    
    
    path('delete_product/<int:id>',views.delete_product,name='delete_product'),
    path('edit_product/<int:id>',views.edit_product,name='edit_product'),
    path('canceled_order/<int:id>',views.canceled_order,name='canceled_order'),
    path('completeorder/<int:id>',views.completeorder,name='completeorder'),
    path('userorder_for_admin',views.userorder_for_admin,name='userorder_for_admin'),
    path('orderdetails_for_manager/<int:id>',views.orderdetails_for_manager,name='orderdetails_for_manager'),

    
    
    
]