from django.db import models


class UrlHit(models.Model):
    """
    One UrlHit object is created per unique URL.  It tracks the total hit count for that URL.
    """

    url = models.URLField()
    hits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.url)

    def increase(self):
        self.hits += 1
        self.save()


class HitCount(models.Model):
    """
    The HitCount model tracks unique hits based on IP address and session key.  Each time a unique combination of IP and session hits a URL,
    a new HitCount object is created.
    """

    url_hit = models.ForeignKey(UrlHit, editable=False, on_delete=models.CASCADE)
    ip = models.CharField(max_length=40)
    session = models.CharField(max_length=40)
    date = models.DateTimeField(auto_now=True)
