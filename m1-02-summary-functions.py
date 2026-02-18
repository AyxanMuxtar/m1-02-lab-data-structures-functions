"""
m1-02-summary-functions.py
--------------------------
This module contains validation and summary functions for the 
support ticket analysis pipeline.
"""

def validate_keys(tickets, required_keys):
    """
    Checks if all tickets contain the specified keys.
    Returns a list of indices where keys are missing.
    """
    missing_key_indices = []
    
    for index, ticket in enumerate(tickets):
        if not set(required_keys).issubset(ticket.keys()):
            missing_key_indices.append(index)
            
    return missing_key_indices

def find_invalid_resolutions(tickets):
    """
    Identifies tickets with non-integer resolution_minutes.
    Returns a list of dictionaries containing the index and the invalid value.
    """
    invalid_records = []
    
    for index, ticket in enumerate(tickets):
        val = ticket.get('resolution_minutes')
        
        # Invalid if it is None OR not an instance of int.
        if val is None or not isinstance(val, int):
            invalid_records.append({
                "index": index,
                "ticket_id": ticket.get('ticket_id', 'UNKNOWN'),
                "invalid_value": val,
                "issue_type": "Missing" if val is None else "Wrong Type"
            })
            
    return invalid_records

def get_average_resolution_by_category(tickets):
    """
    Calculates average resolution time per category.
    Returns a dict: { 'Category': Average_Time }
    """
    temp_stats = {}
    
    for t in tickets:
        cat = t.get('category', 'Unknown')
        mins = t.get('resolution_minutes', 0)
        
        # Ensure we are summing numbers, not strings/None
        if not isinstance(mins, (int, float)):
            continue

        if cat not in temp_stats:
            temp_stats[cat] = {'total': 0, 'count': 0}
            
        temp_stats[cat]['total'] += mins
        temp_stats[cat]['count'] += 1
    
    averages = {}
    for cat, data in temp_stats.items():
        if data['count'] > 0:
            averages[cat] = round(data['total'] / data['count'], 2)
        else:
            averages[cat] = 0
            
    return averages

def get_escalation_rates(tickets):
    """
    Calculates the % of tickets marked as 'Critical' priority.
    Returns a dict with global rate and per-category rates.
    """
    category_counts = {} 
    total_tickets = 0
    total_critical = 0
    
    for t in tickets:
        cat = t.get('category', 'Unknown')
        priority = t.get('priority', 'Low')
        
        is_critical = 1 if priority == 'Critical' else 0
        
        total_tickets += 1
        total_critical += is_critical
        
        if cat not in category_counts:
            category_counts[cat] = {'total': 0, 'critical': 0}
        
        category_counts[cat]['total'] += 1
        category_counts[cat]['critical'] += is_critical

    rates = {
        'overall_rate': 0.0,
        'by_category': {}
    }
    
    if total_tickets > 0:
        rates['overall_rate'] = round((total_critical / total_tickets) * 100, 2)
    
    for cat, data in category_counts.items():
        if data['total'] > 0:
            pct = (data['critical'] / data['total']) * 100
            rates['by_category'][cat] = round(pct, 2)
        
    return rates

def generate_final_report(tickets):
    """
    Combines all summaries into one report dictionary.
    """
    # Note: We call the functions defined above
    report = {
        "meta": {
            "total_records": len(tickets),
            "status": "Success"
        },
        "averages": get_average_resolution_by_category(tickets),
        "escalations": get_escalation_rates(tickets)
    }
    return report