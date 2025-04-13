from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    在模板中根据字典键获取对应的值：
    Usage: {{ my_dict|get_item:my_key }}
    """
    return dictionary.get(key)
