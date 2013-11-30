# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import template
from django.core.urlresolvers import reverse
from django.template import TemplateSyntaxError
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from likes.models import Like

register = template.Library()


class IfLikeNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, *args):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user, self.object_expr = args        

    def render(self, context):
        user = User.objects.get(pk=int(template.resolve_variable(self.user, context)))    
        target_object = self.object_expr.resolve(context)       
        ctype = ContentType.objects.get_for_model(target_object)                     
        if Like.objects.if_user_like_object(user, target_object.pk, ctype):                            
            context['message'] = _("you Like this")
            return self.nodelist_true.render(context) 
        elif Like.objects.if_user_dislike_object(user, target_object.pk, ctype):
            context['message'] = _("you Dislike this")
            return self.nodelist_true.render(context) 
        else:
            #raise template.TemplateSyntaxError('RelationshipStatus not found')                 
            return self.nodelist_false.render(context)   

@register.tag
def if_like(parser, token):
    """
    Determine if a certain type of relationship exists between two users.
    The ``status`` parameter must be a slug matching either the from_slug,
    to_slug or symmetrical_slug of a RelationshipStatus.

    Example::

        {% if_like user object  %}
            messgae
        {% else %}
            Sorry coworkers
        {% endif_like %}
        
    """
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments:\n" % (bits[0], if_like.__doc__)
    object_expr = parser.compile_filter(bits[2])
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()        
    return IfLikeNode(nodelist_true, nodelist_false, bits[1], object_expr)


class LikeItemNode(template.Node):
    """Render a like to like an item"""

    def __init__(self, *args):
        self.object_expr, self.likes = args        


    def render(self, context):        
        target_object = self.object_expr.resolve(context)       
        ctype = ContentType.objects.get_for_model(target_object)   
        return reverse('like_like_item', args=[target_object.pk, ctype.app_label, ctype.model, self.likes])

@register.tag
def like_item(parser, token):
    """
    allow a user to like/dislike an item 

    Example::

        {% like_item object 2/3 %}
    
    where "2" like and "3" dislike
        
    """
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments:\n" % (bits[0], like_item.__doc__)
    object_expr = parser.compile_filter(bits[1])   
    return LikeItemNode(object_expr, bits[2])
 
class LikeCountNode(template.Node):
    """show the number of like for a certain item"""
    def __init__(self, *args):        
        self.object_expr, self.likes = args
    
    def render(self, context):
        target_object = self.object_expr.resolve(context)
        ctype = ContentType.objects.get_for_model(target_object)
        count = Like.objects.count_for_item(target_object.pk, ctype, self.likes)        
        if count.isdigit():
            context['count'] = count
        else:
            context['count'] = 0
        return ''

@register.tag
def like_count(parser, token):
    """
        shows the number of likes/dislikes an item has
        
        example::
            {% like_count object 2/3 %}
                {{ count }}                    
        where "2" like and "3" dislike
    """
    bits = list(token.split_contents())    
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments:\n" % (bits[0], like_count.__doc__)    
    object_expr = parser.compile_filter(bits[1])   
    return LikeCountNode(object_expr, bits[2])

class PeopleLikeThisNode(template.Node):
    """ show a list of people who liked this"""
    def __init__(self, *args):
        self.object_expr, self.likes = args
    
    def render(self, context):
        target_object = self.object_expr.resolve(context)
        ctype = ContentType.objects.get_for_model(target_object)
        context['liker_list'] = Like.objects.people_like_item(pk=target_object.pk, ctype=ctype, likes=self.likes)
        return ''

@register.tag
def people_like_this(parser, token):
    """ show list of user who liked the item 
        example::
        {% people_like_this object 2/3 %}
            {{ liker_list }}
        where "2" like and "3" dislike
    """
    bits = list(token.split_contents())    
    if len(bits) != 3:
        raise TemplateSyntaxError, "%r takes 2 arguments:\n" % (bits[0], people_like_this.__doc__)    
    object_expr = parser.compile_filter(bits[1])   
    return PeopleLikeThisNode(object_expr, bits[2])
