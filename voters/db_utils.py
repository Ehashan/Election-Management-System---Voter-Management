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
    
    print("Database indexes created successfully")
