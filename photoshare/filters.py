from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def truncate_text(text, value):
    if len(text) > value :
        return text[:value] + '...'
    else :
        return text 
    
@register.filter
def is_within_last_day(value) :
    now = datetime.now()
    difference = now - value 
    if isinstance(difference, timedelta) and difference.days == 0 :
        return difference
    return value 

