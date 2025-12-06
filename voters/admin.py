from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from voters.db_utils import get_db, generate_voter_id
from voters.models import RegistrationProxy, VoterProxy
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages

# Customize Admin Site Headers and Titles
admin.site.site_header = "Election Management System Administration"
admin.site.site_title = "EMS Admin Portal"
admin.site.index_title = "Welcome to Election Management System"

# ============================================
# SECTION 1: ADMIN MANAGEMENT
# ============================================

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Login Information', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

# Unregister default and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ============================================
# SECTION 2: USERS (SIGNUP DATA - MongoDB)
# ============================================

class RegistrationAdmin(admin.ModelAdmin):
    """Admin interface for Registration (Signup) data from MongoDB"""
    
    def __init__(self, model, admin_site):
        self.list_display = ['nic', 'name', 'email', 'mobile_number', 'is_mobile_verified', 'verified_at']
        self.list_filter = ['is_mobile_verified']
        self.search_fields = ['nic', 'name', 'email', 'mobile_number']
        self.ordering = ['-user_id']
        super().__init__(model, admin_site)
    
    def has_add_permission(self, request):
        return True  # Admins can add signups
    
    def has_delete_permission(self, request, obj=None):
        return True  # Admins can delete signup records
    
    def has_change_permission(self, request, obj=None):
        return True  # Admins can update signup data
    
    def get_queryset(self, request):
        """Fetch data from MongoDB Registration collection"""
        db = get_db()
        registrations = list(db.Registration.find())
        return registrations
    
    def changelist_view(self, request, extra_context=None):
        """Display list of registrations from MongoDB"""
        db = get_db()
        registrations = list(db.Registration.find().sort('user_id', -1))
        
        # Format data for display
        formatted_data = []
        for reg in registrations:
            formatted_data.append({
                '_id': str(reg.get('_id')),
                'user_id': reg.get('user_id'),
                'nic': reg.get('nic'),
                'name': reg.get('name'),
                'email': reg.get('email'),
                'mobile_number': reg.get('mobile_number'),
                'is_mobile_verified': '✓ Yes' if reg.get('is_mobile_verified') else '✗ No',
                'verified_at': reg.get('verified_at', 'Not verified'),
            })
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Users (Signup Data)',
            'registrations': formatted_data,
            'has_add_permission': self.has_add_permission(request),
        }
        
        return render(request, 'admin/registration_list.html', context)

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            nic = request.POST.get('nic')
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            
            if nic and name:
                try:
                    db = get_db()
                    db.Registration.insert_one({
                        'nic': nic,
                        'name': name,
                        'email': email,
                        'mobile_number': mobile,
                        'is_mobile_verified': True,  # Admin added, assume verified
                        'verified_at': datetime.now(),
                        'user_id': None # Or generate one
                    })
                    messages.success(request, f'User {name} added successfully.')
                    return redirect('admin:voters_registrationproxy_changelist')
                except Exception as e:
                    messages.error(request, f'Error adding user: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Add User Signup',
            'opts': self.model._meta, # Required for admin breadcrumbs
            'has_view_permission': True,
        }
        return render(request, 'admin/add_registration.html', context)

# ============================================
# SECTION 3: VOTERS (FULL REGISTRATION - MongoDB)
# ============================================

class VoterAdmin(admin.ModelAdmin):
    """Admin interface for Voters (Full Registration) data from MongoDB"""
    
    def __init__(self, model, admin_site):
        self.list_display = ['voter_id', 'name', 'nic', 'admin_district', 'election_district', 'registration_status']
        self.list_filter = ['admin_district', 'election_district', 'gender', 'registration_status']
        self.search_fields = ['voter_id', 'nic', 'name', 'email']
        self.ordering = ['-registered_at']
        super().__init__(model, admin_site)
    
    def has_add_permission(self, request):
        return True  # Admins can add voters
    
    def has_delete_permission(self, request, obj=None):
        return True  # Admins can delete voter records
    
    def has_change_permission(self, request, obj=None):
        return True  # Admins can update voter data
    
    def get_queryset(self, request):
        """Fetch data from MongoDB voters collection"""
        db = get_db()
        voters = list(db.voters.find())
        return voters
    
    def changelist_view(self, request, extra_context=None):
        """Display list of voters from MongoDB"""
        db = get_db()
        voters = list(db.voters.find().sort('registered_at', -1))
        
        # Format data for display
        formatted_data = []
        for voter in voters:
            formatted_data.append({
                '_id': str(voter.get('_id')),
                'voter_id': voter.get('voter_id', 'N/A'),
                'nic': voter.get('nic'),
                'name': voter.get('name'),
                'email': voter.get('email'),
                'date_of_birth': voter.get('date_of_birth', 'N/A'),
                'gender': voter.get('gender', 'N/A'),
                'admin_district': voter.get('admin_district', 'N/A'),
                'election_district': voter.get('election_district', 'N/A'),
                'polling_division': voter.get('polling_division', 'N/A'),
                'registration_status': voter.get('registration_status', 'Pending'),
                'registered_at': voter.get('registered_at', 'N/A'),
            })
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Voters (Registration Data)',
            'voters': formatted_data,
            'has_add_permission': self.has_add_permission(request),
        }
        
        return render(request, 'admin/voter_list.html', context)

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            nic = request.POST.get('nic')
            name = request.POST.get('name')
            district = request.POST.get('admin_district')
            
            if nic and name and district:
                try:
                    # Generate Voter ID
                    voter_id = generate_voter_id(district)
                    
                    db = get_db()
                    db.voters.insert_one({
                        'voter_id': voter_id,
                        'nic': nic,
                        'name': name,
                        'email': request.POST.get('email'),
                        'date_of_birth': request.POST.get('dob'),
                        'gender': request.POST.get('gender'),
                        'admin_district': district,
                        'election_district': request.POST.get('election_district'),
                        'polling_division': request.POST.get('polling_division'),
                        'registration_status': 'Verified', # Admin added
                        'registered_at': datetime.now(),
                        'face_image_data': None,
                        'user_id': None # Admin added, no linked user account yet
                    })
                    messages.success(request, f'Voter {name} added successfully with ID {voter_id}.')
                    return redirect('admin:voters_voterproxy_changelist')
                except Exception as e:
                    messages.error(request, f'Error adding voter: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Add New Voter',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/add_voter.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        db = get_db()
        voter = db.voters.find_one({'voter_id': object_id})
        
        if not voter:
            messages.error(request, 'Voter not found.')
            return redirect('admin:voters_voterproxy_changelist')

        if request.method == 'POST':
            try:
                update_data = {
                    'nic': request.POST.get('nic'),
                    'name': request.POST.get('name'),
                    'email': request.POST.get('email'),
                    'date_of_birth': request.POST.get('dob'),
                    'gender': request.POST.get('gender'),
                    'admin_district': request.POST.get('admin_district'),
                    'election_district': request.POST.get('election_district'),
                    'polling_division': request.POST.get('polling_division'),
                    'registration_status': request.POST.get('registration_status'),
                }
                
                db.voters.update_one({'voter_id': object_id}, {'$set': update_data})
                messages.success(request, f'Voter {object_id} updated successfully.')
                return redirect('admin:voters_voterproxy_changelist')
            except Exception as e:
                messages.error(request, f'Error updating voter: {str(e)}')

        context = {
            **self.admin_site.each_context(request),
            'title': f'Change Voter: {object_id}',
            'voter': voter,
            'opts': self.model._meta,
            'has_change_permission': True,
            'original': voter,
        }
        return render(request, 'admin/change_voter_v2.html', context)

    def delete_view(self, request, object_id, extra_context=None):
        if request.method == 'POST':
            try:
                db = get_db()
                db.voters.delete_one({'voter_id': object_id})
                messages.success(request, f'Voter {object_id} deleted successfully.')
                return redirect('admin:voters_voterproxy_changelist')
            except Exception as e:
                messages.error(request, f'Error deleting voter: {str(e)}')
        
        context = {
            **self.admin_site.each_context(request),
            'title': f'Are you sure?',
            'object_name': f'Voter {object_id}',
            'object': object_id,
            'opts': self.model._meta,
            'has_delete_permission': True,
        }
        return render(request, 'admin/delete_confirmation_custom.html', context)

# Register MongoDB-backed models
admin.site.register(RegistrationProxy, RegistrationAdmin)
admin.site.register(VoterProxy, VoterAdmin)
