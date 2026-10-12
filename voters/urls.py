from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.voter_signup, name='voter_signup'),
    path('check-nic/', views.check_nic, name='check_nic'),
    path('verify/', views.mobile_verification, name='mobile_verification'),
    path('signin/', views.voter_signin, name='voter_signin'),
    path('logout/', views.user_logout, name='logout'),
    path('registration/', views.voter_registration, name='voter_registration'),
    path('admin-login/', views.admin_login, name='admin_login'),
    
    # Informational Nav Pages
    path('citizens/', views.citizens_page, name='citizens'),
    path('officers/', views.officers_page, name='officers'),
    path('parties/', views.parties_page, name='parties'),
    path('services/', views.services_page, name='services'),
    path('services/check-status/', views.check_status, name='check_status'),
    
    # Custom Admin URLs
    path('custom-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/voters/', admin_views.admin_voter_list, name='admin_voter_list'),
    path('custom-admin/voters/add/', admin_views.admin_add_voter, name='admin_add_voter'),
    path('custom-admin/voters/edit/<str:voter_id>/', admin_views.admin_edit_voter, name='admin_edit_voter'),
    path('custom-admin/voters/delete/<str:voter_id>/', admin_views.admin_delete_voter, name='admin_delete_voter'),
    
    # Signup Management
    path('custom-admin/signups/', admin_views.admin_signup_list, name='admin_signup_list'),
    path('custom-admin/signups/delete/<str:nic>/', admin_views.admin_delete_signup, name='admin_delete_signup'),
]
