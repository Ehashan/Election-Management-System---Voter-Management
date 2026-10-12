"""
Module for public aggregate electoral statistics.
Calculates aggregate metrics without exposing any personal voter data (no NIC, name, photo, etc.).
"""
from .db_utils import get_db

def get_public_stats():
    """
    Compute aggregate public voter statistics only (strictly NO personal data).
    Returns a dict with:
    - total_voters: int
    - approved_voters: int
    - pending_voters: int
    - district_data: list of dicts [{'district', 'count', 'pct_total', 'bar_pct'}]
    - gender_data: list of dicts [{'gender', 'count', 'pct'}]
    - total_districts_count: int
    """
    total_voters = 0
    approved_voters = 0
    pending_voters = 0
    district_data = []
    gender_data = []
    total_districts_count = 0

    try:
        db = get_db()
        # Count total voters (documents in voters collection with valid ID or any record)
        total_voters = db.voters.count_documents({'voter_id': {'$nin': [None, '']}})
        if total_voters == 0:
            total_voters = db.voters.count_documents({})

        # Approved voters: 'Verified' or 'Approved'
        approved_voters = db.voters.count_documents({'registration_status': {'$in': ['Verified', 'Approved']}})

        # Pending approvals: 'Pending' or awaiting verification ('completed')
        pending_voters = db.voters.count_documents({'registration_status': {'$in': ['Pending', 'completed']}})

        # If any records have unassigned status or total differs, account for them in pending
        if total_voters > 0 and (approved_voters + pending_voters) < total_voters:
            unaccounted = total_voters - (approved_voters + pending_voters)
            pending_voters += unaccounted

        # Top 10 election districts
        district_pipeline = [
            {'$match': {'election_district': {'$nin': [None, '']}}},
            {'$group': {'_id': '$election_district', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        district_results = list(db.voters.aggregate(district_pipeline))
        total_districts_count = len(db.voters.distinct('election_district'))

        max_district_count = max([d.get('count', 0) for d in district_results], default=0)

        for d in district_results:
            d_name = d.get('_id') or 'Unknown'
            count = d.get('count', 0)
            pct_total = round((count / total_voters * 100), 1) if total_voters > 0 else 0
            bar_pct = round((count / max_district_count * 100), 1) if max_district_count > 0 else 0
            district_data.append({
                'district': d_name,
                'count': count,
                'pct_total': pct_total,
                'bar_pct': max(bar_pct, 6) if count > 0 else 0
            })

        # Gender split
        gender_pipeline = [
            {'$match': {'gender': {'$nin': [None, '']}}},
            {'$group': {'_id': '$gender', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        gender_results = list(db.voters.aggregate(gender_pipeline))
        gender_total = sum(g.get('count', 0) for g in gender_results)

        for g in gender_results:
            g_name = g.get('_id') or 'Other'
            count = g.get('count', 0)
            pct = round((count / gender_total * 100), 1) if gender_total > 0 else 0
            gender_data.append({
                'gender': g_name,
                'count': count,
                'pct': pct
            })

    except Exception:
        # Gracefully handle database or connection error by retaining 0/empty values
        pass

    return {
        'total_voters': total_voters,
        'approved_voters': approved_voters,
        'pending_voters': pending_voters,
        'district_data': district_data,
        'gender_data': gender_data,
        'total_districts_count': total_districts_count,
    }
