from django.contrib import admin
from django.urls import path, include
from pdfapp.views import home
from pdfapp import views, pseudomyzation_views
from pdfapp import views, tokenization_views


urlpatterns = [
    path('', home, name='home'),
    path('tokenize/', tokenization_views.tokenize, name='tokenize'),
    path('pseudo/', pseudomyzation_views.pseudo, name='pseudo'),
    path('admin/', admin.site.urls),
]
