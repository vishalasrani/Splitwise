from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Group, GroupMember
from .serializers import (
    GroupSerializer,
    GroupCreateSerializer,
    GroupUpdateSerializer,
    GroupMemberSerializer
)

User = get_user_model()


class IsGroupMember(permissions.BasePermission):
    """Permission to check if user is a member of the group"""
    
    def has_object_permission(self, request, view, obj):
        return obj.members.filter(id=request.user.id).exists()


class IsGroupCreatorOrMember(permissions.BasePermission):
    """Permission to check if user is creator or member of the group"""
    
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or obj.members.filter(id=request.user.id).exists()


class GroupViewSet(ModelViewSet):
    """
    ViewSet for Group CRUD operations.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = None  # Using get_queryset() instead

    def get_serializer_class(self):
        if self.action == 'create':
            return GroupCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return GroupUpdateSerializer
        return GroupSerializer

    def get_queryset(self):
        """Return only groups where user is a member"""
        return Group.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        """Create group with current user as creator"""
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'create']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsGroupCreatorOrMember]
        else:
            permission_classes = [permissions.IsAuthenticated, IsGroupMember]
        
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsGroupMember])
    def add_member(self, request, pk=None):
        """Add a member to the group"""
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate user_id is a valid integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return Response(
                {'error': 'user_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            group_member, created = GroupMember.objects.get_or_create(
                group=group,
                user=user
            )
            
            if created:
                return Response(
                    {
                        'message': f'{user.email} added to group successfully',
                        'member': GroupMemberSerializer(group_member).data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': f'{user.email} is already a member of this group'},
                    status=status.HTTP_200_OK
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'], permission_classes=[IsGroupCreatorOrMember])
    def remove_member(self, request, pk=None):
        """Remove a member from the group"""
        group = self.get_object()
        user_id = request.data.get('user_id') or request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate user_id is a valid integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return Response(
                {'error': 'user_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent removing the creator
        if user_id == group.created_by.id:
            return Response(
                {'error': 'Cannot remove group creator'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            group_member = GroupMember.objects.get(group=group, user=user)
            group_member.delete()
            
            return Response(
                {'message': f'{user.email} removed from group successfully'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except GroupMember.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this group'},
                status=status.HTTP_404_NOT_FOUND
            )
