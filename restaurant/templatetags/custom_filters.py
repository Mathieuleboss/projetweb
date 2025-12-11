from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def split(value, arg):
    """Divise une chaîne en liste"""
    return value.split(arg)

@register.filter
def index(list_obj, i):
    """Récupère un élément d'une liste par son index"""
    try:
        return list_obj[int(i)]
    except (IndexError, TypeError, ValueError):
        return ''
