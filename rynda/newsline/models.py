# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Post(models.Model):
    """ One site news item """

    DRAFT = 0
    PUBLISHED = 1

    STATUS = ((DRAFT, _("draft")), (PUBLISHED, _("published")))

    title = models.CharField(max_length=200, verbose_name=_("title"))
    post = models.TextField(verbose_name=_("Post"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True)
    publish = models.DateTimeField(_("Publish"), default=datetime.datetime.now)
    status = models.IntegerField(_("Status"), choices=STATUS)
    author = models.ForeignKey(User, verbose_name=_("Author"),)
