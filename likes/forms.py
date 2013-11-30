# -*- coding: utf-8 -*-
import datetime
from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from models import Like
from django.utils.encoding import force_unicode
from django.utils.translation import ungettext, ugettext_lazy as _
from django.contrib.comments.forms import CommentSecurityForm



class LikeDetailsForm(CommentSecurityForm):
    """
    Handles the specific details of the like (name, like, etc.).
    """
    likes = forms.CharField(max_length=1)

    def get_like_object(self):
        """
        Return a new (unsaved) like object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError("get_like_object may only be called on valid forms")

        likeModel = self.get_like_model()
        new = likeModel(**self.get_like_create_data())

        return new

    def get_like_model(self):
        """
        Get the like model to create with this form. Subclasses in custom
        like apps should override this, get_like_create_data, and perhaps
        check_for_duplicate_like to provide custom like models.
        """
        return Like

    def get_like_create_data(self):
        """
        Returns the dict of data to be used to create a like. Subclasses in
        custom like apps that override get_like_model can override this
        method to add extra fields onto a custom like model.
        """
        return dict(
            content_type=ContentType.objects.get_for_model(self.target_object),
            object_pk=force_unicode(self.target_object._get_pk_val()),
            likes=self.cleaned_data["likes"],
            submit_date=datetime.datetime.now(),
            site_id=settings.SITE_ID,
            is_public=True,
            is_removed=False,
        )

class LikeForm(LikeDetailsForm):
    honeypot = forms.CharField(required=False,
                                    label=_('If you enter anything in this field '\
                                            'your like will be treated as spam'))

    def clean_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value
