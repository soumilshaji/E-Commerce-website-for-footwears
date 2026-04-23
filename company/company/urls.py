from django.contrib import admin 
from django.urls import path,include 
from employee import views 
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns = [ 
    path('admin/', admin.site.urls), 
    path('',include('employee.urls')), 
    path('',include('manager.urls')), 
] 

urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'employee.views.custom_404'