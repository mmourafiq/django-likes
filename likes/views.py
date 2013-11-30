# -*- coding: utf-8 -*-
# Create your views here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.html import escape
from django.contrib.auth.decorators import login_required
from django.contrib.comments.views.utils import *
import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from models import Like
if 'notification' in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class LikePostBadRequest(HttpResponseBadRequest):
    """
    Response returned when a comment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """
    def __init__(self, why):
        super(LikePostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-debug.html", {"why": why})
            


@csrf_exempt
@requires_csrf_token
@login_required
def like_item(request, object_pk, app_label, model, likes):
    """render_to_response
    like an object view
    """       
    # Look up the object we're trying to like
    try:
        ctype = ContentType.objects.get(app_label=app_label, model=model)
        model = ctype.model_class()
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return LikePostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return LikePostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return LikePostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError), e:
        return LikePostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))


    request_user = request.user
    # Otherwise create the like
    like = Like.objects.filter(user=request_user, content_type=ctype, object_pk=object_pk)
    if like.count() > 0:
        like = like[0]
    else:
        like = Like()    
        
    
    like.ip_address = request.META.get("REMOTE_ADDR", None)    
    like.user = request_user
    like.content_type = ctype
    like.object_pk = object_pk
    like.likes = likes
    like.submit_date = datetime.datetime.now()
    like.site_id = settings.SITE_ID

    # Save the like and signal that it was saved
    like.save()
    if notification:
        #notify all concerned users by the object             
        notification.send([request_user], "new_like", {'like_user': request_user, 
                                                       'like_object':target,})    
#    signals.like_was_posted.send(
#        sender=like.__class__,
#        like=like,
#        request=request
#    )
    if request.is_ajax():
        json_response = simplejson.dumps({
                'success': True,
                'like_user': request_user.username, })
        return HttpResponse(json_response, mimetype="application/json")
        
    return HttpResponseRedirect('/')


def get_list_likers(request, object_pk, app_label, model, likes):
    # Look up the object we're trying to like
    try:
        ctype = ContentType.objects.get(app_label=app_label, model=model)
        model = ctype.model_class()
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return LikePostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return LikePostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return LikePostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError), e:
        return LikePostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))
            
    c = RequestContext(request, {'target':target,
                                 'likes':likes,                                 
                                 }) 
    return render_to_response('likes/_like_list.html', c)


def get_like_count(request, object_pk, app_label, model, likes):    
    # Look up the object we're trying to like
    try:
        ctype = ContentType.objects.get(app_label=app_label, model=model)
        model = ctype.model_class()
        target = model._default_manager.get(pk=object_pk)
    except TypeError:
        return LikePostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return LikePostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return LikePostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError), e:
        return LikePostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))
        
    c = RequestContext(request, {'target':target,
                                 'likes':likes,                                 
                                 }) 
    return render_to_response('likes/_like_count.html', c)
