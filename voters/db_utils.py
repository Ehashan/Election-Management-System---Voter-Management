from pymongo import MongoClient
from django.conf import settings
from datetime import datetime

def get_db():
    try:
        import dns.resolver
        dns.resolver.get_default_resolver().nameservers = ['8.8.8.8', '1.1.1.1']
    except Exception:
        pass
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    return db

# District code mapping for unique voter ID generation
DISTRICT_CODES = {
    'Ampara': 'AMP', 'Anuradhapura': 'ANU', 'Badulla': 'BAD',
    'Batticaloa': 'BAT', 'Colombo': 'COL', 'Galle': 'GAL',
    'Gampaha': 'GAM', 'Hambantota': 'HAM', 'Jaffna': 'JAF',
    'Kalutara': 'KAL', 'Kandy': 'KAN', 'Kegalle': 'KEG',
    'Kilinochchi': 'KIL', 'Kurunegala': 'KUR', 'Mannar': 'MAN',
    'Matale': 'MAT', 'Matara': 'MTR', 'Monaragala': 'MON',
    'Mullaitivu': 'MUL', 'Nuwara Eliya': 'NUW', 'Polonnaruwa': 'POL',
    'Puttalam': 'PUT', 'Ratnapura': 'RAT', 'Trincomalee': 'TRI',
    'Vavuniya': 'VAV'
}

def generate_voter_id(district, year=None):
    """
    Generate unique voter ID in format: {DISTRICT_CODE}-{YEAR}-{SEQUENTIAL}
    Example: COL-2025-000001
    """
    if year is None:
        year = datetime.now().year
    else:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = datetime.now().year
    
    district_code = DISTRICT_CODES.get(district, 'UNK')
    db = get_db()
    voters_collection = db['voters']
    
    # Find the highest sequential number for this district and year
    prefix = f"{district_code}-{year}-"
    last_voter = voters_collection.find_one(
        {'voter_id': {'$regex': f'^{prefix}'}},
        sort=[('voter_id', -1)]
    )
    
    if last_voter and 'voter_id' in last_voter:
        # Extract sequential number and increment
        last_id = last_voter['voter_id']
        last_seq = int(last_id.split('-')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    # Format: DISTRICT-YEAR-NNNNNN (6 digits)
    voter_id = f"{district_code}-{year}-{new_seq:06d}"
    return voter_id

def check_voter_registered(user_id):
    """Check if user has completed detailed registration"""
    db = get_db()
    voters_collection = db['voters']
    voter = voters_collection.find_one({'user_id': user_id})
    return voter is not None

def initialize_db_indexes():
    """Create indexes for better performance"""
    db = get_db()
    
    # Registration collection indexes
    db.Registration.create_index('nic', unique=True)
    db.Registration.create_index('user_id', unique=True)
    db.Registration.create_index('mobile_number')
    
    # Voters collection indexes
    db.voters.create_index('voter_id', unique=True)
    db.voters.create_index('user_id', unique=True)
    db.voters.create_index('nic', unique=True)
    db.voters.create_index([('admin_district', 1), ('election_year', 1)])
    
    # temp_nic collection indexes
    db.temp_nic.create_index('nic', unique=True)
    
    print("Database indexes created successfully")

# 50 Pre-generated random valid Sri Lankan NIC numbers (25 Old format + 25 New format)
SAMPLE_TEMP_NICS = [
    # 25 Old format (9 digits + V)
    "781423589V", "792154687V", "803215498V", "811564789V", "822453698V",
    "833125478V", "841789654V", "852468135V", "863579246V", "871357924V",
    "882468013V", "893579124V", "901452369V", "912563478V", "923674589V",
    "931478523V", "942589631V", "953691472V", "961472583V", "972583691V",
    "983694715V", "991592634V", "876543210V", "915432167V", "948765432V",
    # 25 New format (12 digits)
    "198512304561", "198623405672", "198734506783", "198845607894", "198956708905",
    "199012304567", "199123405678", "199234506789", "199345607890", "199456708901",
    "199512307892", "199623408903", "199734509014", "199845601235", "199956702346",
    "200012303457", "200123404568", "200234505679", "200345606780", "200456707891",
    "200512308902", "199467801234", "199678902345", "199889003456", "200190104567"
]

def seed_temp_nics(overwrite=False):
    """
    Populate temp_nic collection with 50 valid Sri Lankan NIC numbers.
    """
    db = get_db()
    if overwrite:
        db.temp_nic.delete_many({})
    
    inserted_count = 0
    for nic in SAMPLE_TEMP_NICS:
        existing = db.temp_nic.find_one({'nic': nic})
        if not existing:
            db.temp_nic.insert_one({
                'nic': nic,
                'is_used': False,
                'created_at': datetime.now(),
                'used_at': None,
                'user_id': None
            })
            inserted_count += 1
            
    db.temp_nic.create_index('nic', unique=True)
    return inserted_count, len(SAMPLE_TEMP_NICS)

def validate_temp_nic(nic):
    """
    Validates a NIC against the temp_nic collection.
    Returns: (is_valid: bool, status: str, message: str)
    Statuses:
      - 'invalid_format'
      - 'invalid_nic'
      - 'already_used'
      - 'available'
    """
    import re
    from django.contrib.auth.models import User
    
    if not nic:
        return False, 'invalid_nic', 'NIC is required.'
    
    nic_clean = nic.strip().upper()
    
    old_format = re.match(r'^[0-9]{9}[VX]$', nic_clean)
    new_format = re.match(r'^[0-9]{12}$', nic_clean)
    if not (old_format or new_format):
        return False, 'invalid_format', 'Invalid NIC format. Use 9 digits + V (e.g., 123456789V) or 12 digits (e.g., 199912345678)'
    
    db = get_db()
    temp_record = db.temp_nic.find_one({'nic': {'$regex': f'^{re.escape(nic_clean)}$', '$options': 'i'}})
    
    if not temp_record:
        return False, 'invalid_nic', 'Invalid NIC. This NIC does not exist in the official records.'
    
    # Check if already used
    is_temp_used = temp_record.get('is_used', False)
    has_django_user = User.objects.filter(username__iexact=nic_clean).exists()
    has_registration = db.Registration.find_one({'nic': {'$regex': f'^{re.escape(nic_clean)}$', '$options': 'i'}}) is not None
    
    if is_temp_used or has_django_user or has_registration:
        return False, 'already_used', 'NIC already used. This NIC has already been registered.'
    
    return True, 'available', 'Valid NIC'

def mark_temp_nic_status(nic, is_used=True, user_id=None):
    """Mark a NIC in temp_nic as used or unused."""
    import re
    if not nic:
        return
    nic_clean = nic.strip().upper()
    db = get_db()
    update_fields = {'is_used': is_used}
    if is_used:
        update_fields['used_at'] = datetime.now()
        if user_id:
            update_fields['user_id'] = user_id
    else:
        update_fields['used_at'] = None
        update_fields['user_id'] = None
        
    db.temp_nic.update_one(
        {'nic': {'$regex': f'^{re.escape(nic_clean)}$', '$options': 'i'}},
        {'$set': update_fields}
    )

