from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return value * arg
    except (ValueError, TypeError):
        return 0
