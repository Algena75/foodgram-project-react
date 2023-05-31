from django.http import QueryDict
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (ChangePasswordSerializer, FollowSerializer,
                             SignupSerializer, UserSerializer)
from users.models import Follow, User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return UserSerializer
        return SignupSerializer

    @action(
        detail=False, methods=['get', ],
        url_path='me', url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def about_me(self, request):
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        serializer = SignupSerializer(data=data)
        if isinstance(data, QueryDict):
            data = data.dict()
        if User.objects.filter(**data).exists():
            return Response(
                'Учетная запись существует',
                status=status.HTTP_200_OK
            )
        if serializer.is_valid():
            user = User.objects.create(
                **serializer.validated_data
            )
            user.set_password(serializer.validated_data.get('password'))
            user.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False, methods=['post', ],
        url_path='set_password', url_name='pw',
        permission_classes=(IsAuthenticated,)
    )
    def change_password(self, request):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=self.request.data)

        if serializer.is_valid():
            if not user.check_password(
                serializer.data.get('current_password')
            ):
                return Response(
                    {'current_password': 'Неправильный пароль.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response(
                {'message': 'Password updated successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        obj = get_object_or_404(Follow, user=user, author=author)
        obj.delete()
        return Response(
            {'message': 'Подписка удалена!'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=['get', ],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = self.paginate_queryset(
            queryset=User.objects.filter(following__user=user),
        )
        serializer = FollowSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
