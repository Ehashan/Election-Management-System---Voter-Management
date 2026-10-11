from django.shortcuts import render, redirect
from django.contrib import messages
from .decorators import admin_required
from .db_utils import get_db, generate_voter_id, DISTRICT_CODES
from datetime import datetime

@admin_required
def admin_dashboard(request):
    """
    Main dashboard for the custom admin interface.
    Displays statistics and quick links.
    """
    db = get_db()
    
    # Fetch statistics
    total_voters = db.voters.count_documents({})
    total_signups = db.Registration.count_documents({})
    verified_voters = db.voters.count_documents({'registration_status': 'Verified'})
    pending_voters = db.voters.count_documents({'registration_status': 'Pending'})
    
    context = {
        'total_voters': total_voters,
        'total_signups': total_signups,
        'verified_voters': verified_voters,
        'pending_voters': pending_voters,
        'title': 'Admin Dashboard'
    }
    return render(request, 'custom_admin/dashboard.html', context)

@admin_required
def admin_voter_list(request):
    """
    List all voters with search functionality.
    """
    db = get_db()
    # Base query to ensure valid voter_id
    base_query = {'voter_id': {'$nin': [None, '']}}
    
    search_term = request.GET.get('search', '')
    if search_term:
        query = {
            '$and': [
                base_query,
                {
                    '$or': [
                        {'name': {'$regex': search_term, '$options': 'i'}},
                        {'nic': {'$regex': search_term, '$options': 'i'}},
                        {'voter_id': {'$regex': search_term, '$options': 'i'}}
                    ]
                }
            ]
        }
    else:
        query = base_query
    
    voters = list(db.voters.find(query).sort('registered_at', -1))
    
    context = {
        'voters': voters,
        'search_term': search_term,
        'title': 'Manage Voters'
    }
    return render(request, 'custom_admin/voter_list.html', context)

def _extract_image(request):
    """Helper to extract face image from webcam base64 or uploaded file"""
    img_data = request.POST.get('face_image_data')
    if img_data and img_data.strip():
        return img_data.strip()
    if request.FILES.get('face_image_file'):
        import base64
        uploaded_file = request.FILES.get('face_image_file')
        content = uploaded_file.read()
        b64 = base64.b64encode(content).decode('utf-8')
        mime = uploaded_file.content_type or 'image/jpeg'
        return f"data:{mime};base64,{b64}"
    return None

@admin_required
def admin_add_voter(request):
    """
    Add a new voter manually directly by admin without requiring prior user registration.
    """
    from .forms import VoterRegistrationForm
    
    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            db = get_db()
            
            # Check if a voter with this NIC already exists
            existing_voter = db.voters.find_one({'nic': data.get('nic')})
            if existing_voter:
                form.add_error('nic', f"A voter with NIC {data.get('nic')} is already registered (Voter ID: {existing_voter.get('voter_id')}).")
                context = {
                    'form': form,
                    'title': 'Add New Voter'
                }
                return render(request, 'custom_admin/voter_form.html', context)
            
            # Generate Voter ID
            admin_district = data.get('admin_district')
            election_year = data.get('election_year')
            voter_id = generate_voter_id(admin_district, election_year)
            
            data['voter_id'] = voter_id
            data['registered_at'] = datetime.now()
            data['registration_status'] = 'Verified' # Admin added is verified by default
            data['user_id'] = None # Added directly by admin without prior user account
            
            # Handle Face Image
            face_img = _extract_image(request)
            if face_img:
                data['face_image'] = face_img
            
            # Convert date to string
            if data.get('date_of_birth'):
                data['date_of_birth'] = data['date_of_birth'].isoformat()
            
            try:
                db.voters.insert_one(data)
                messages.success(request, f'Voter {data.get("name")} added successfully with ID: {voter_id}')
                return redirect('admin_voter_list')
            except Exception as e:
                messages.error(request, f'Error adding voter: {str(e)}')
    else:
        form = VoterRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Add New Voter'
    }
    return render(request, 'custom_admin/voter_form.html', context)

@admin_required
def admin_edit_voter(request, voter_id):
    """
    Edit an existing voter.
    """
    from .forms import VoterRegistrationForm
    
    db = get_db()
    voter = db.voters.find_one({'voter_id': voter_id})
    
    if not voter:
        messages.error(request, 'Voter not found.')
        return redirect('admin_voter_list')
    
    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            
            # Preserve original ID and registration data
            data['voter_id'] = voter_id
            data['user_id'] = voter.get('user_id')
            data['registered_at'] = voter.get('registered_at')
            status = request.POST.get('registration_status')
            if status:
                data['registration_status'] = status
            else:
                data['registration_status'] = voter.get('registration_status', 'Verified')
            
            # Handle Face Image (update if new provided, otherwise keep existing)
            new_image = _extract_image(request)
            if new_image:
                data['face_image'] = new_image
            elif voter.get('face_image'):
                data['face_image'] = voter.get('face_image')
            
            # Convert date
            if data.get('date_of_birth'):
                data['date_of_birth'] = data['date_of_birth'].isoformat()
            
            try:
                db.voters.update_one({'voter_id': voter_id}, {'$set': data})
                messages.success(request, 'Voter updated successfully.')
                return redirect('admin_voter_list')
            except Exception as e:
                messages.error(request, f'Error updating voter: {str(e)}')
    else:
        # Pre-fill form
        initial_data = voter.copy()
        if 'date_of_birth' in initial_data and isinstance(initial_data['date_of_birth'], str):
             try:
                 initial_data['date_of_birth'] = datetime.fromisoformat(initial_data['date_of_birth']).date()
             except:
                 pass
                 
        form = VoterRegistrationForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': f'Edit Voter: {voter_id}',
        'voter_id': voter_id,
        'current_image': voter.get('face_image'),
        'current_status': voter.get('registration_status', 'Verified'),
        'is_edit': True
    }
    return render(request, 'custom_admin/voter_form.html', context)

@admin_required
def admin_delete_voter(request, voter_id):
    """
    Delete a voter.
    """
    db = get_db()
    
    if request.method == 'POST':
        try:
            db.voters.delete_one({'voter_id': voter_id})
            messages.success(request, f'Voter {voter_id} deleted successfully.')
            return redirect('admin_voter_list')
        except Exception as e:
            messages.error(request, f'Error deleting voter: {str(e)}')
            return redirect('admin_voter_list')
            
    voter = db.voters.find_one({'voter_id': voter_id})
    if not voter:
        messages.error(request, 'Voter not found.')
        return redirect('admin_voter_list')
        
    context = {
        'voter': voter,
        'title': 'Delete Voter'
    }
    return render(request, 'custom_admin/delete_confirm.html', context)

@admin_required
def admin_signup_list(request):
    """
    List all user signups (Registration collection).
    """
    db = get_db()
    query = {}
    
    search_term = request.GET.get('search', '')
    if search_term:
        query = {
            '$or': [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'nic': {'$regex': search_term, '$options': 'i'}},
                {'email': {'$regex': search_term, '$options': 'i'}}
            ]
        }
    
    users = list(db.Registration.find(query).sort('registered_at', -1))
    
    context = {
        'users': users,
        'search_term': search_term,
        'title': 'Manage Signups'
    }
    return render(request, 'custom_admin/signup_list.html', context)

@admin_required
def admin_delete_signup(request, nic):
    """
    Delete a user signup.
    """
    db = get_db()
    
    if request.method == 'POST':
        try:
            # Delete from Registration collection
            db.Registration.delete_one({'nic': nic})
            
            # Delete from Django User model
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(username=nic)
                user.delete()
            except User.DoesNotExist:
                pass
                
            messages.success(request, f'Signup for {nic} deleted successfully.')
            return redirect('admin_signup_list')
        except Exception as e:
            messages.error(request, f'Error deleting signup: {str(e)}')
            return redirect('admin_signup_list')
            
    signup = db.Registration.find_one({'nic': nic})
    if not signup:
        messages.error(request, 'Signup not found.')
        return redirect('admin_signup_list')
        
    context = {
        'signup': signup,
        'title': 'Delete Signup'
    }
    return render(request, 'custom_admin/delete_signup_confirm.html', context)
