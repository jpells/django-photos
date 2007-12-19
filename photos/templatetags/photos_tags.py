from django.template import Library, Node
from photos.models import Photo
register = Library()

class LatestPhotoNode(Node):
    def __init__(self, context_var):
        self.context_var = context_var
    def render(self, context):
        context[self.context_var] = Photo.objects.order_by('-pub_date')[:5]
        return ''

def latest_photos(parser, token):
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError('%s tag requires exactly two arguments' % bits[0])
    if bits[1] != 'as':
        raise TemplateSyntaxError("first argument to %s tag must be 'as'" % bits[0])
    return LatestPhotoNode(bits[2])

register.tag('latest_photos', latest_photos)
