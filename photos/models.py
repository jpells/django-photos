from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from photos.FlickrClient import FlickrClient
from django.utils.translation import ugettext as _
from django.conf import settings

class PhotoManager(models.Manager):
    def sync_flickr_photos(*args, **kwargs):
        cur_page = 1            # Start on the first page of the stream
        paginate_by = 20        # Get 20 photos at a time
        dupe = False            # Set our dupe flag for the following loop
        client = FlickrClient(settings.FLICKR_API_KEY)          # Get our flickr client running
        while (not dupe):
            photos = client.flickr_people_getPublicPhotos(user_id=settings.FLICKR_USER_ID, page=cur_page, per_page=paginate_by)
            for photo in photos:
                try:
                    row = Photo.objects.get(flickr_id=photo("id"), flickr_secret=str(photo("secret")))
                    # Raise exception if photo doesn't exist in our DB yet
                    # If the row exists already, set the dupe flag
                    dupe = True
                except ObjectDoesNotExist:
                    p = Photo(
                        title = str(photo("title")),
                        flickr_id = int(photo("id")),
                        flickr_owner = str(photo("owner")),
                        flickr_server = int(photo("server")),
                        flickr_secret = str(photo("secret")),
                    )
                    p.save()
                    if (dupe or photos("page") == photos("pages")):   # If we hit a dupe or if we did the last page...
                        break
                else:
                    cur_page += 1

class Photo(models.Model):
    title = models.CharField(blank=True, max_length=100)
    flickr_id = models.IntegerField()
    flickr_owner = models.CharField(max_length=20)
    flickr_server = models.IntegerField()
    flickr_secret = models.CharField(max_length=50)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Published"))
    objects = PhotoManager()
   
    class Admin:
        list_display = ('title',)

    def __unicode__(self):
        return _(self.title)
        
    def get_absolute_url(self):
        return "http://flickr.com/photos/%s/%s/" % (settings.FLICKR_USER_ID, self.flickr_id)

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
