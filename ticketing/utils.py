import uuid

def generate_ticket_id():
    return f"TKT-{str(uuid.uuid4())[:8]}"