from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import VoterSignupForm, VoterRegistrationForm
from .db_utils import get_db, generate_voter_id, check_voter_registered
from pymongo.errors import OperationFailure
import random
from datetime import datetime, timedelta


def home(request):
    return render(request, 'home.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def voter_signup(request):
    if request.method == 'POST':
        form = VoterSignupForm(request.POST)
        if form.is_valid():
            nic = form.cleaned_data['nic']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            mobile = form.cleaned_data['mobile_number']
            
            # Create User in Django
            user = User.objects.create_user(username=nic, email=email, password=password)
            user.first_name = name
            user.save()
            
            # Save basic signup info to Registration collection
            try:
                db = get_db()
                result = db.Registration.insert_one({
                    'user_id': user.id,
                    'nic': nic,
                    'name': name,
                    'email': email,
                    'mobile_number': mobile,
                    'is_mobile_verified': False
                })
                print(f"DEBUG: Inserted to Registration collection with ID: {result.inserted_id}")
            except OperationFailure as e:
                user.delete()
                error_msg = f"Database Error: {e.details.get('errmsg', str(e))}. Admin: Check MONGO_URI in settings.py."
                form.add_error(None, error_msg)
                return render(request, 'voter_signup.html', {'form': form})
            except Exception as e:
                user.delete()
                form.add_error(None, f"Unexpected error: {str(e)}")
                return render(request, 'voter_signup.html', {'form': form})
            
            # Generate Verification Code
            verification_code = str(random.randint(100000, 999999))
            code_expiry = datetime.now() + timedelta(seconds=settings.VERIFICATION_CODE_EXPIRY)
            
            request.session['verification_code'] = verification_code
            request.session['verifying_user_id'] = user.id
            request.session['verifying_mobile'] = mobile
            request.session['code_expiry'] = code_expiry.isoformat()
            
            print(f"DEBUG: Verification Code for {mobile}: {verification_code}")
            print(f"DEBUG: Code expires at: {code_expiry}")
            
            
            return redirect('mobile_verification')
    else:
        form = VoterSignupForm()
    
    return render(request, 'voter_signup.html', {'form': form})

def mobile_verification(request):
    session_code = request.session.get('verification_code', 'No code found')
    mobile_number = request.session.get('verifying_mobile', '')
    code_expiry_str = request.session.get('code_expiry')
    
    # Check if code has expired
    code_expired = False
    if code_expiry_str:
        code_expiry = datetime.fromisoformat(code_expiry_str)
        if datetime.now() > code_expiry:
            code_expired = True
    
    if request.method == 'POST':
        # Handle resend request
        if request.POST.get('resend'):
            # Generate new code
            new_code = str(random.randint(100000, 999999))
            new_expiry = datetime.now() + timedelta(seconds=settings.VERIFICATION_CODE_EXPIRY)
            
            request.session['verification_code'] = new_code
            request.session['code_expiry'] = new_expiry.isoformat()
            
            print(f"DEBUG: New Verification Code: {new_code}")
            
            return render(request, 'mobile_verification.html', {
                'debug_code': new_code,
                'mobile_number': mobile_number,
                'success': 'New verification code generated!'
            })
        
        # Handle code verification
        code = request.POST.get('code')
        user_id = request.session.get('verifying_user_id')
        
        if code_expired:
            return render(request, 'mobile_verification.html', {
                'error': 'Verification code has expired. Please request a new code.',
                'debug_code': session_code,
                'mobile_number': mobile_number,
                'code_expired': True
            })
        
        if code == session_code and user_id:
            user = User.objects.get(id=user_id)
            
            # Update Registration collection
            db = get_db()
            db.Registration.update_one(
                {'user_id': user.id}, 
                {'$set': {'is_mobile_verified': True, 'verified_at': datetime.now()}}
            )
            
            # Clear session data
            request.session.pop('verification_code', None)
            request.session.pop('verifying_user_id', None)
            request.session.pop('verifying_mobile', None)
            request.session.pop('code_expiry', None)
            
            # Set success message for signin page
            request.session['verification_success'] = True
            request.session['verified_nic'] = user.username
            
            # Redirect to signin page (user must sign in manually)
            return redirect('voter_signin')
        else:
            return render(request, 'mobile_verification.html', {
                'error': 'Invalid verification code. Please try again.',
                'debug_code': session_code,
                'mobile_number': mobile_number
            })
            
    return render(request, 'mobile_verification.html', {
        'debug_code': session_code,
        'mobile_number': mobile_number,
        'code_expired': code_expired
    })


def voter_signin(request):
    # Check if user just completed verification
    verification_success = request.session.pop('verification_success', False)
    verified_nic = request.session.pop('verified_nic', '')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('voter_registration')
    else:
        form = AuthenticationForm()
    
    return render(request, 'voter_signin.html', {
        'form': form,
        'verification_success': verification_success,
        'verified_nic': verified_nic
    })


def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                form.add_error(None, "Your account does not have admin privileges.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'admin_login.html', {'form': form})

@login_required
def voter_registration(request):
    db = get_db()
    voters_collection = db['voters']
    registration_collection = db['Registration']
    
    # Check if detailed profile exists
    profile_data = voters_collection.find_one({'user_id': request.user.id})
    
    # Get registration data for pre-filling
    reg_data = registration_collection.find_one({'user_id': request.user.id})
    
    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Get updated name and NIC from form (editable fields)
            updated_name = data.get('name')
            updated_nic = data.get('nic')
            
            # Add/update user info
            data['user_id'] = request.user.id
            data['email'] = request.user.email
            
            # Update Django User if name or NIC changed
            if updated_name != request.user.first_name:
                request.user.first_name = updated_name
                request.user.save()
            
            # Handle Face Image
            face_image_data = request.POST.get('face_image_data')
            if not face_image_data:
                form.add_error(None, "Please capture your face image before submitting.")
                return render(request, 'voter_registration.html', {
                    'form': form,
                    'user': request.user,
                    'profile': profile_data
                })
            
            data['face_image'] = face_image_data
            
            # Convert date to string for Mongo
            if data.get('date_of_birth'):
                data['date_of_birth'] = data['date_of_birth'].isoformat()
            
            # Generate unique voter ID if not exists
            if not profile_data or 'voter_id' not in profile_data:
                admin_district = data.get('admin_district')
                election_year = data.get('election_year')
                voter_id = generate_voter_id(admin_district, int(election_year))
                data['voter_id'] = voter_id
                print(f"DEBUG: Generated Voter ID: {voter_id}")
            else:
                data['voter_id'] = profile_data['voter_id']
            
            # Add registration timestamp
            data['registered_at'] = datetime.now()
            data['registration_status'] = 'completed'
            
            # Save detailed registration to voters collection
            voters_collection.update_one(
                {'user_id': request.user.id},
                {'$set': data},
                upsert=True
            )
            
            print(f"DEBUG: Saved detailed registration to voters collection for user {request.user.id}")
            print(f"DEBUG: Voter ID: {data['voter_id']}")
            
            return render(request, 'registration_success.html', {
                'user': request.user,
                'voter_id': data['voter_id']
            })
    else:
        # Pre-fill form with existing data
        initial_data = {}
        
        if profile_data:
            initial_data = profile_data.copy()
        else:
            # Pre-fill from registration data
            if reg_data:
                initial_data['name'] = reg_data.get('name', request.user.first_name)
                initial_data['nic'] = reg_data.get('nic', request.user.username)
        
        form = VoterRegistrationForm(initial=initial_data)
    
    return render(request, 'voter_registration.html', {
        'form': form,
        'user': request.user,
        'profile': profile_data
    })
