# -*- coding: utf-8 -*-
from django.contrib.comments.managers import CommentManager

class LikeManager(CommentManager):
    
    def if_user_like_object(self, user, pk, ctype):        
        if self.filter(user=user, content_type=ctype, object_pk=pk, likes="2", is_removed=False).count() > 0:
            return True
        return False
    
    def if_user_dislike_object(self, user, pk, ctype):        
        if self.filter(user=user, content_type=ctype, object_pk=pk, likes="3", is_removed=False).count() > 0:
            return True
        return False
    
    def count_for_item(self, pk, ctype, likes):
        count = self.filter(content_type=ctype, object_pk=pk, likes=likes, is_removed=False).count()
        if count > 0:
            return str(count)
        else :
            return ''        
            
    def people_like_item(self, pk, ctype, likes):
        list = self.filter(content_type=ctype, object_pk=pk, likes=likes, is_removed=False)
        if list.count() > 0:
            return list
        else:
            return ''
