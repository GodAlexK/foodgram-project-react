import base64

from django.db.models import F

from django.db import IntegrityError
from django.shortcuts import get_object_or_404


from rest_framework.exceptions import ValidationError

from django.core.files.base import ContentFile
from django.contrib.auth.validators import UnicodeUsernameValidator

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User, Subscription
from recipes import models
from users.validators import validate_username

RECIPES_LIMIT = 6

class RecipeForUserSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для сериализатора пользователей."""

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    username = serializers.CharField(
        required=True, max_length=150,
        validators=[validate_username, UnicodeUsernameValidator()]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            )

    def validate(self, data):
        """Запрещает пользователям присваивать себе username me
        и использовать повторные username и email."""
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


class CustomUserSerializer(UserSerializer):
    """Сериализатор для проверки подписки пользователя."""
    
    is_subscribed=serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            )

    def validate(self, data):
        """Запрещает пользователям присваивать себе username me
        и использовать повторные username и email."""
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data

    def get_is_subscribed(self, object):
        """Проверяет, подписан ли текущий пользователь на автора аккаунта."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.author.filter(subscriber=request.user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    class Meta:
        model = Subscription
        fields = (
            'subscriber',
            'author',
            )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'subscriber'),
                message='Вы уже подписывались на этого автора'
            )
        ]

    def validate(self, data):
        """Проверяем, что пользователь не подписывается на самого себя."""
        if data['subscriber'] == data['author']:
            raise serializers.ValidationError(
                'Подписка на cамого себя не имеет смысла'
            )
        return data


class SubscriptionShowSerializer(CustomUserSerializer):

    """Сериализатор отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
            'recipes_count'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.root.context.get('request')
        if request is not None:
            count = request.query_params.get('recipes_limit')
        else:
            count = self.root.context.get('recipes_limit')
        if count is not None:
            rep['recipes'] = rep['recipes'][:int(count)]
        return rep


    def get_recipes(self, object):
        author_recipes= object.recipes.all()[:RECIPES_LIMIT]
        return RecipeForUserSerializer(
            author_recipes, many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = models.Tag
        fields = '__all__'
        read_only_fields = ('slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""

    class Meta:
        model = models.Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            )

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    @staticmethod
    def validate_amount(value):
        """Метод валидации количества"""

        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value


    class Meta:
        model = models.RecipeIngredient
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    """Сериализатор для поля картинки в формате Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)

class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    color = serializers.CharField()
    slug = serializers.SlugField()

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    name = serializers.CharField(max_length=200)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()


    class Meta:
        exclude = ('favorites', 'shopping_cart')
        model = models.Recipe

    def validate(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {
                    'ingredients': (
                        'Необходимо указать хотя бы один ингредиент.'
                    )
                }
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                {'tags', ('Необходимо указать хотя бы один тег.')}
            )
        return data

    def validate_ingredients(self, value):
        """Проверка, что ингредиент не повторяется"""
        ingredients_ids = [ingredient['id'] for ingredient in value]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                ('Ингредиенты не должны повторяться.')
            )
        return value

    def validate_cooking_time(self, value):
        """Проверка что время приготовления больше 0"""
        if value < 1:
            raise serializers.ValidationError(
                ('Время приготовления должно быть больше 0.')
            )
        return value

    def validate_tags(self, value):
        """Проверка что теги не повторяются"""
        if not value:
            raise serializers.ValidationError(
                ('Необходимо указать хотя бы один тег')
            )
        tags = [tag.id for tag in value]
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(('Теги не должны повторяться.'))
        return value

    def add_ingredients(self, recipe, ingredients):
        """Создает ингредиенты для рецепта"""
        try:
            models.RecipeIngredient.objects.bulk_create(
                models.RecipeIngredient(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        models.Ingredient, id=ingredient['id']
                    ),
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            )
        except IntegrityError as error:
            raise ValidationError(
                (f'Ошибка при добавлении ингредиента: {error}')
            )


    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.add_ingredients(instance, ingredients)
        instance.save()
        return instance


class RecipeSerializer(RecipeCreateSerializer):
    """Сериализатор рецептов!!"""

    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=200)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'text',
            'cooking_time',
            'image',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('recipes_ingredients__amount'))


    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorites.filter(pk=obj.pk).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(pk=obj.pk).exists()
        return False
