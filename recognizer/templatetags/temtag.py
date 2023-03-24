from django import template

register = template.Library()

@register.simple_tag
def current_pk(request):
    try:
        return  request.user.user_profile.pk
    except:
        return None
    