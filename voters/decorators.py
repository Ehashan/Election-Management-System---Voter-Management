from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """
    Decorator to ensure the user is an authenticated superuser.
    Redirects to admin login if not authenticated or not a superuser.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access the admin panel.")
            return redirect('admin_login')
        
        if not request.user.is_superuser:
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('home')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
