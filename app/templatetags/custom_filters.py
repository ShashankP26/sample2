from django import template
from app.models import SubModuleVisibility

register = template.Library()

@register.filter
def is_submodule_visible(user, submodule):
    try:
        visibility = SubModuleVisibility.objects.get(user=user, submodule=submodule)
        return visibility.is_visible
    except SubModuleVisibility.DoesNotExist:
        return False


# app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Splits a string by a given separator (arg)."""
    return value.split(arg)


from django import template

register = template.Library()

@register.filter
def add_class(value, arg):
    """
    Adds a CSS class to a form field.
    Usage: {{ form.field_name|add_class:"my-class" }}
    """
    return value.as_widget(attrs={'class': arg})