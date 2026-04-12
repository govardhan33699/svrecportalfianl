from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def days_until(value):
    if not value:
        return ""
    from datetime import date, datetime
    today = date.today()
    
    # Handle both date and datetime objects
    if isinstance(value, datetime):
        target_date = value.date()
    else:
        target_date = value
        
    diff = (target_date - today).days
    
    if diff == 0:
        return "Today"
    elif diff > 0:
        return f"{diff} Days Left"
    else:
        return f"{abs(diff)} Days Ago"

