# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User
from likes.managers import LikeManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.models import BaseCommentAbstractModel

LIKE_STATUS = (
    ("1", "NONE"),
    ("2", "LIKE"),
    ("3", "DISLIKE")
)


class Like(BaseCommentAbstractModel):
    """
    A user like or dislike about some object.
    """

    # Who liked or disliked? 
    # only authenticated users have the right to like or not the object
    
    user = models.ForeignKey(User, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_comments")    
    likes = models.CharField(max_length=1, choices=LIKE_STATUS)

    # Metadata about the comment
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True)
    is_public = models.BooleanField(_('is public'), default=True,
                    help_text=_('Uncheck this box to make the comment effectively ' \
                                'disappear from the site.'))
    is_removed = models.BooleanField(_('is removed'), default=False,
                    help_text=_('Check this box if the comment is inappropriate. ' \
                                'A "This comment has been removed" message will ' \
                                'be displayed instead.'))

    # Manager
    objects = LikeManager()

    class Meta:                    
        #we can add permisssions after word permissions = [("can_moderate", "Can moderate comments")]
        verbose_name = _('like')
        verbose_name_plural = _('likes')

    def __unicode__(self):
        return self.user.username        

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
        super(Like, self).save(*args, **kwargs)


    
    def get_absolute_url(self, anchor_pattern="#c%(id)s"):
        return self.get_content_object_url() + (anchor_pattern % self.__dict__)
    
    def get_as_text(self):
        """
        Return this comment as plain text.  Useful for emails.
        """
        d = {
            'user': self.user,
            'date': self.submit_date,
            'like': self.likes,
            'domain': self.site.domain,
        }
        if d['likes'] == "2":
            return _('liked by %(user)s at %(date)s\n\n%(like)s\n\nhttp://%(domain)s%(url)s') % d
        elif d['likes'] == "3":
            return _('disliked by %(user)s at %(date)s\n\n%(like)s\n\nhttp://%(domain)s%(url)s') % d

class LikeFlag(models.Model):
    """
    Records a flag on a likes. This is intentionally flexible; right now, a
    flag could be:

        * A "removal suggestion" -- where a user suggests a comment for (potential) removal.

        * A "moderator deletion" -- used when a moderator deletes a comment.

    You can (ab)use this model to add other flags, if needed. However, by
    design users are only allowed to flag a comment with a given flag once;
    if you want rating look elsewhere.
    """
    user = models.ForeignKey(User, verbose_name=_('user'), related_name="like_flags")
    likes = models.ForeignKey(Like, verbose_name=_('like'), related_name="flags")
    flag = models.CharField(_('flag'), max_length=30, db_index=True)
    flag_date = models.DateTimeField(_('date'), default=None)

    # Constants for flag types
    SUGGEST_REMOVAL = "removal suggestion"
    MODERATOR_DELETION = "moderator deletion"
    MODERATOR_APPROVAL = "moderator approval"

    class Meta:
        db_table = 'like_flags'
        unique_together = [('user', 'likes', 'flag')]
        verbose_name = _('like flag')
        verbose_name_plural = _('like flags')

    def __unicode__(self):
        return "%s flag of like ID %s by %s" % \
            (self.flag, self.like_id, self.user.username)

    def save(self, *args, **kwargs):
        if self.flag_date is None:
            self.flag_date = datetime.datetime.now()
        super(LikeFlag, self).save(*args, **kwargs)
