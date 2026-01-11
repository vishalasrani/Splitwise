from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """
    Group model for shared expenses.
    Users can create groups and add members to share expenses.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_groups'
    )
    members = models.ManyToManyField(
        User,
        through='GroupMember',
        related_name='user_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groups'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    """
    Intermediate model for Group-User relationship.
    Tracks when a user joined a group.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_members'
        unique_together = ['group', 'user']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.email} in {self.group.name}"
