from django import template

register =template.Library()

#@register.filter(name= 'add_class')
#def add_class(field, css_class):
#    """Adding a CSS class to form fields"""
#    return field.as_widget(attrs= {"class": css_class})

#@register(name="add_class")
@register.filter
def add_class(field, css_class= "default-class"):
    #if hasattr(field, 'field') and 'attrs' in field.field.widget.attrs:
    #    field.field.widget.attrs['class'] += f" {css_class}"
    #else:
    #    field.widget.attrs = {"class": css_class}
    return field.as_widget(attrs={"class": css_class})

"""
    Adds a CSS class to form field widgets.
    :param field: The form field
    :param css_class: The CSS class to add
    :return: The field with the additional CSS class
"""