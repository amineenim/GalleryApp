from django import template

register =template.Library()

@register.filter

def truncate_text(text, value):
    if len(text) > value :
        return text[:value] + '...'
    else :
        return text 
    

