# -*- coding: utf-8 -*-

from flask import url_for
from . import db, BaseMixin, BaseScopedNameMixin, VotingMixin, CommentingMixin
from .profile import Profile
from hasweb.models import commentease


__all__ = ['Workspace', 'WorkspaceFunnel', 'WorkspaceSchedule']


class WORKSPACE_FLAGS:
    FUNNEL = 1
    SCHEDULE = 2
    FORUM = 4


workspace_types = {
    1: u"Funnel",
    2: u"Schedule",
    4: u"Forum"
}


class FUNNEL_STATUS:
    DRAFT = 1
    OPEN = 2
    CLOSED = 3


funnel_status = {
    1: u"Draft",
    2: u"Open",
    3: u"Closed",
}


class Workspace(BaseScopedNameMixin, db.Model):
    __tablename__ = 'workspace'

    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship(Profile)
    parent = db.synonym('profile')

    description = db.Column(db.UnicodeText, default=u"", nullable=False)

    feature_flags = db.Column(db.Integer, default=0, nullable=False)

    @property
    def has_funnel(self):
        return True if self.feature_flags & WORKSPACE_FLAGS.FUNNEL else False

    @property
    def has_schedule(self):
        return True if self.feature_flags & WORKSPACE_FLAGS.SCHEDULE else False

    @property
    def has_forum(self):
        return True if self.feature_flags & WORKSPACE_FLAGS.FORUM else False

    def enable_funnel(self):
        if not self.funnel:
            self.funnel = WorkspaceFunnel(workspace=self)
            db.session.add(self.funnel)
        self.feature_flags |= WORKSPACE_FLAGS.FUNNEL

    def disable_funnel(self):
        if self.funnel:
            db.session.delete(self.funnel)
        self.funnel = None
        self.feature_flags &= ~WORKSPACE_FLAGS.FUNNEL

    def enable_schedule(self):
        if not self.schedule:
            self.schedule = WorkspaceSchedule(workspace=self)
            db.session.add(self.schedule)
        self.feature_flags |= WORKSPACE_FLAGS.SCHEDULE

    def disable_schedule(self):
        if self.schedule:
            db.session.delete(self.schedule)
        self.schedule = None
        self.feature_flags &= ~WORKSPACE_FLAGS.SCHEDULE

    def enable_forum(self):
        if not self.forum:
            self.forum = WorkspaceForum(workspace=self)
            db.session.add(self.forum)
        self.feature_flags |= ~WORKSPACE_FLAGS.FORUM

    def disable_forum(self):
        if self.forum:
            db.session.delete(self.forum)
        self.forum = None
        self.feature_flags &= ~WORKSPACE_FLAGS.FORUM

    def permissions(self, user, inherited=None):
        perms = super(Workspace, self).permissions(user, inherited)
        return perms

    def url_for(self, action='view'):
        if action == 'view':
            return url_for('workspace', profile=self.profile.name, workspace=self.name)


class WorkspaceFunnel(BaseMixin, db.Model):
    __tablename__ = 'workspace_funnel'
    workspace_id = db.Column(None, db.ForeignKey('workspace.id'), nullable=False)
    workspace = db.relationship(Workspace, backref=db.backref('funnel', cascade='all, delete-orphan'))

    status = db.Column(db.Integer, default=FUNNEL_STATUS.DRAFT, nullable=False)
    proposal_template = db.Column(db.UnicodeText, default=u"", nullable=False)

    def __init__(self, **kwargs):
        super(WorkspaceFunnel, self).__init__(**kwargs)

    def is_open(self):
        return self.status == FUNNEL_STATUS.OPEN


class WorkspaceSchedule(BaseMixin, db.Model):
    __tablename__ = 'workspace_schedule'
    workspace_id = db.Column(None, db.ForeignKey('workspace.id'), nullable=False)
    workspace = db.relationship(Workspace, backref=db.backref('schedule', cascade='all, delete-orphan'))


class WorkspaceForum(BaseMixin, db.Model):
    __tablename__ = 'workspace_forum'
    workspace_id = db.Column(None, db.ForeignKey('workspace.id'), nullable=False)
    workspace = db.relationship(Workspace, backref=db.backref('forum', cascade='all, delete-orphan'))
