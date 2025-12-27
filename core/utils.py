from datetime import date, timedelta

def get_member_status(member, grace_days=4):
    today = date.today()
    grace = timedelta(days=grace_days)

    if today <= member.end_date:
        return "active", "green"
    elif today <= member.end_date + grace:
        return "grace", "orange"
    else:
        return "expired", "red"
