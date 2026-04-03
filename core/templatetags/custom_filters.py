from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def split(value, arg):
    """Split a string by the given separator."""
    if not value:
        return []
    try:
        return [item.strip() for item in value.split(arg)]
    except (ValueError, TypeError, AttributeError):
        return [value]

@register.filter
def strip(value):
    """Strip whitespace from both ends of a string."""
    if not value:
        return value
    try:
        return value.strip()
    except (ValueError, TypeError, AttributeError):
        return value
