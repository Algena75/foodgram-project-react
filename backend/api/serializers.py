import base64
import re

from django.core.files.base import ContentFile
from django.db.models import F
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ValidateUserSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        if not re.match(r'[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                f'{value} содержит запрещённые символы.'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Имя пользователя не может быть больше 150 символов.'
            )
        return value


class UserSerializer(ValidateUserSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'pk',
            'username',
            'first_name',
            'last_name',
        )

    def get_is_subscribed(self, obj):
        user = self.context['view'].request.user
        if not user.is_authenticated or user == obj:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class SignupSerializer(ValidateUserSerializer):

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('password', 'email')


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(IngredientSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('created',)

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        if not value:
            raise ValidationError(
                {'tags': 'Это поле обязательно!'}
            )
        check_list = []
        for tag in value:
            if tag in check_list:
                raise ValidationError(
                    {'tags': 'Теги должны быть уникальными!'}
                )
            check_list.append(tag)
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(
                {'ingredients': 'Это поле обязательно!'}
            )
        check_list = []
        for ingredient in value:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise ValidationError(
                    {f'Ингредиента с id {ingredient["id"]} нет в базе!'}
                )
            if ingredient in check_list:
                raise ValidationError(
                    {'ingredients': 'Ингредиенты не должны повторяться!'}
                )
            if int(ingredient['amount']) <= 0:
                raise ValidationError({
                    'amount':
                    'Убедитесь, что это значение больше либо равно 1.'
                })
            check_list.append(ingredient)
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        if instance.author != self.context.get('request').user:
            raise ValidationError(
                {'message': 'Редактировать может только автор'},
                code=status.HTTP_400_BAD_REQUEST
            )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=instance,
                amount=ingredient['amount']
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class ShortRecipeSerializer(RecipeSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True, )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                {'message': 'Такая подписка уже существует'},
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                {'message': 'Нельзя подписаться на себя'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_is_subscribed(self, obj):
        return True
