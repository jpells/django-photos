from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from photos.FlickrClient import FlickrClient
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import User
from tagging.fields import TagField
from published_manager.managers import PublishedManager
from django.template.defaultfilters import slugify

class FlickrUser(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), null=True, blank=True)
    flickr_id = models.CharField(max_length=12, verbose_name=_("Flickr Id"))

    class Admin:
        pass

    def __unicode__(self):
        return _("%s %s" % (self.user.__unicode__(), self.flickr_id))

    def sync_photos(self):
        cur_page = 1
        paginate_by = 20
        dupe = False
        client = FlickrClient(settings.FLICKR_API_KEY)
        while (not dupe):
            photos = client.flickr_people_getPublicPhotos(user_id=self.flickr_id, page=cur_page, per_page=paginate_by)
            for photo in photos:
                try:
                    row = Photo.objects.get(flickr_id=photo("id"), flickr_secret=str(photo("secret")))
                    dupe = True
                except ObjectDoesNotExist:
                    p = Photo(
                        title = str(photo("title")),
                        flickr_id = int(photo("id")),
                        flickr_server = int(photo("server")),
                        flickr_secret = str(photo("secret")),
                        slug = slugify(str(photo("title"))),
                        state = settings.STATE_DEFAULT,
                        flickr_user = self,
                    )
                    p.save()
                    if (dupe or photos("page") == photos("pages")):
                        break
                else:
                    cur_page += 1

class Photo(models.Model):
    title = models.CharField(blank=True, max_length=100)
    flickr_id = models.IntegerField()
    flickr_server = models.IntegerField()
    flickr_secret = models.CharField(max_length=50)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Published"))
    flickr_user = models.ForeignKey(FlickrUser, verbose_name=_("Flickr User"))
    state = models.CharField(max_length=1, choices=settings.STATE_CHOICES, default=settings.STATE_DEFAULT, verbose_name=_("State of object"))
    ip_address = models.IPAddressField(verbose_name=_("Author's IP Address"), null=True, blank=True)
    tags = TagField(help_text=_("Enter key terms seperated with a space that you want to associate with this Entry"), verbose_name=_("Tags"))
    slug = models.SlugField(prepopulate_from=('title',), unique=True, verbose_name=_("Slug Field"))
    published_objects = PublishedManager()
    objects = models.Manager()

    class Admin:
        list_display = ('title',)

    def __unicode__(self):
        return _(self.title)
        
    def get_absolute_url(self):
        return "http://flickr.com/photos/%s/%s/" % (self.flickr_user.flickr_id, self.flickr_id)

    def get_pic_url(self, size='thumb'):
	    # small_square=75x75
    	# thumb=100 on longest side
	    # small=240 on longest side
    	# medium=500 on longest side
	    # large=1024 on longest side
    	# original=duh
        base_url = "http://static.flickr.com"
        size_char='s'  # default to small_square
        if size == 'small_square':
            size_char='_s'
        elif size == 'thumb':
            size_char='_t'
        elif size == 'small':
            size_char='_m'
        elif size == 'medium':
            size_char=''
        elif size == 'large':
            size_char='_b'
        elif size == 'original':
            size_char='_o'
        return "%s/%s/%s_%s%s.jpg" % (base_url, self.flickr_server, self.flickr_id, self.flickr_secret, size_char)
