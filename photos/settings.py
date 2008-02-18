"""
Convenience module for access of custom photo application settings,
which enforces default settings when the main settings module does not
contain the appropriate settings.
"""
from django.conf import settings

_ = lambda s: s

# The key in order to use Flickr API
FLICKR_API_KEY = getattr(settings, 'FLICKR_API_KEY', '')

# The choices for state of a Photo
STATE_CHOICES = getattr(settings, 'STATE_CHOICES', (
    ('1', _('Draft')),
    ('2', _('Published')),
    ('3', _('Inactive')),
))

# The default state when a Photo is created
STATE_DEFAULT = getattr(settings, 'STATE_DEFAULT', 3)

# The state of a Published Photo
STATE_PUBLISHED = getattr(settings, 'STATE_PUBLISHED', 2)