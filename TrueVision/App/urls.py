from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard, name='dashboard'),
    path('',views.Home, name='homepage'),
    path('signin/',views.Signin, name='signin'),
     path('api/signup/', views.signup_view, name='signup'),
    path('api/login/', views.login_view, name='login'),
    path('api/text/analyze/', views.analyze_text, name='analyze_text'),
    path('api/image/analyze/', views.analyze_image, name='analyze_image'),
    path('api/image/history/', views.image_history, name='image_history'),
    path('api/text/history/', views.text_history, name='text_history'), 
]
