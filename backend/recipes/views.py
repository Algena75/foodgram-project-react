from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (IngredientSerializer, RecipeSerializer,
                             RecipeWriteSerializer, ShortRecipeSerializer,
                             TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    list_filter = ['tags', ]
    http_method_names = ['get', 'post', 'delete', 'patch']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, instance, *args, **kwargs):
        instance = self.get_object()
        if instance.author != self.request.user:
            return Response(
                {"detail": "У вас нет прав для выполнения данного действия."},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(
            'Рецепт успешно удалён.',
            status=status.HTTP_204_NO_CONTENT
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeWriteSerializer

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if obj.exists():
                return Response(
                    {'message': 'Рецепт уже есть в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipeSerializer(recipe)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if obj.exists():
            obj.delete()
            return Response(
                {'message': 'Рецепт удалён из избранного!'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': 'Такого рецепта нет в вашем избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if obj.exists():
                return Response(
                    {'message': 'Рецепт уже есть в списке покупок!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ShortRecipeSerializer(recipe)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if obj.exists():
            obj.delete()
            return Response(
                {'message': 'Рецепт удалён из списка покупок!'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': 'Такого рецепта нет в вашем списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False, methods=['get', ],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.buyer.exists():
            return Response(
                {'message': 'Список покупок не найден'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__in_cart__user=user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum('amount')
        )
        data_file = 'Список покупок\n\n'
        for ingredient in ingredients_list:
            data_file += '- '.join([
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["amount"]}\n']
            )
        filename = f'{user}_shopping_cart.txt'
        response = HttpResponse(data_file, content_type='text/plain')
        response['Content-Disposition'] = f'attachement; filename={filename}'
        return response
