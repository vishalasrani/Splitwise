from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Group, GroupMember

User = get_user_model()


class GroupMemberSerializer(serializers.ModelSerializer):
    """Serializer for group member details"""
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = GroupMember
        fields = ('id', 'user_id', 'email', 'first_name', 'last_name', 'joined_at')
        read_only_fields = ('id', 'joined_at')


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    members = GroupMemberSerializer(source='group_members', many=True, read_only=True)
    member_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = Group
        fields = (
            'id', 'name', 'description', 'created_by', 'created_by_email',
            'created_by_name', 'members', 'member_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def get_created_by_name(self, obj):
        """Get full name of creator"""
        if obj.created_by.first_name or obj.created_by.last_name:
            return f"{obj.created_by.first_name or ''} {obj.created_by.last_name or ''}".strip()
        return obj.created_by.email


class GroupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a group"""
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of user IDs to add as members"
    )

    class Meta:
        model = Group
        fields = ('name', 'description', 'member_ids')

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        # created_by is passed via serializer.save(created_by=...) in perform_create
        # validated_data.pop('created_by', None)
        group = Group.objects.create(
            # created_by=self.context['request'].user,  # Passed via validated_data from perform_create
            **validated_data
        )
        
        # Add creator as a member
        GroupMember.objects.get_or_create(group=group, user=group.created_by)
        
        # Add other members
        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                GroupMember.objects.get_or_create(group=group, user=user)
            except User.DoesNotExist:
                pass  # Skip invalid user IDs
        
        return group


class GroupUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating group details"""
    class Meta:
        model = Group
        fields = ('name', 'description')

