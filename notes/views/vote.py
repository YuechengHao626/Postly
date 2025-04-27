from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from ..models import Vote, Post, Comment
from ..serializers import VoteSerializer

class VoteCreateAPIView(CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate that target exists
        target_type = serializer.validated_data['target_type']
        target_id = serializer.validated_data['target_id']
        
        try:
            if target_type == 'post':
                Post.objects.get(id=target_id)
            elif target_type == 'comment':
                Comment.objects.get(id=target_id)
        except ObjectDoesNotExist:
            return Response(
                {'detail': f'Target {target_type} with id {target_id} does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Try to get existing vote or create new one
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            target_type=target_type,
            target_id=target_id,
            defaults={'value': 'like'}
        )

        # Return the serialized vote data
        response_serializer = self.get_serializer(vote)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        ) 