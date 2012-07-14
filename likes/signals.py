# -*- coding: utf-8 -*-
'''
Created on May 01, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
"""
Signals relating to likes.
"""
from django.dispatch import Signal

# Sent just before a like will be posted (after it's been approved and
# moderated; this can be used to modify the like (in place) with posting
# details or other such actions. If any receiver returns False the like will be
# discarded and a 403 (not allowed) response. This signal is sent at more or less
# the same time (just before, actually) as the like object's pre-save signal,
# except that the HTTP request is sent along with this signal.
like_will_be_posted = Signal(providing_args=["like", "request"])

# Sent just after a like was posted. See above for how this differs
# from the like object's post-save signal.
like_was_posted = Signal(providing_args=["like", "request"])

# Sent after a like was "flagged" in some way. Check the flag to see if this
# was a user requesting removal of a like, a moderator approving/removing a
# like, or some other custom user flag.
like_was_flagged = Signal(providing_args=["like", "flag", "created", "request"])
