from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard, name='dashboard'),
    path('',views.Home, name='homepage'),
    path('signin/',views.Signin, name='signin'),
     path('api/signup/', views.signup_view, name='signup'),
    path('api/login/', views.login_view, name='login'),
    path('api/text/analyze/', views.analyze_text, name='analyze_text'),
    path('api/text/history/', views.text_history, name='text_history'),
    path('api/image/analyze/', views.analyze_image, name='analyze_image'),
    path('api/image/history/', views.image_analysis_history, name='image_analysis_history'),
    path('api/document/analyze/', views.analyze_document, name='analyze_document'),
    path('api/document/history/', views.document_analysis_history, name='document_history'),
    path('api/integrity/check/', views.integrity_check, name='integrity_check'),
    path('api/integrity/history/', views.integrity_check_history, name='integrity_history'),
    path('api/stats/', views.get_user_stats, name='stats'),
    path('api/files/', views.get_all_files, name='all_files'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/users/', views.get_all_users, name='all_users'),
    path('api/admin/text/history/', views.admin_text_history, name='admin_text_history'),
    path('api/admin/document/history/', views.admin_document_history, name='admin_document_history'),
    path('api/admin/image/history/', views.admin_image_history, name='admin_image_history'),
    path('api/admin/integrity/history/', views.admin_integrity_history, name='admin_integrity_history'),
    path('logout/', views.logout_view, name='logout'),
    
]
