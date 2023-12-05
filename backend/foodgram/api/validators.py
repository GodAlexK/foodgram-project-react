import re

from rest_framework import serializers, status

from recipes.models import Tag
from users.models import Subscription


class ValidateUser(object):
    def validate_username(self, username):
        text = "Недопустимый username: "
        if username == "me":
            raise serializers.ValidationError(text + username)
        if re.match(r"^[\w.@+-]+\Z", username) is None:
            raise serializers.ValidationError(text + username)
        return username


def validate_subscription(author, user):
    if author == user:
        return {
            "errors": "Нельзя подписываться на самого себя",
            "status": status.HTTP_400_BAD_REQUEST,
        }
    if Subscription.objects.filter(user=user, author=author).exists():
        return {
            "errors": "Подписка уже оформлена",
            "status": status.HTTP_400_BAD_REQUEST,
        }


class ValidateTags(object):
    def validate_slug(self, slug):
        text = " -содержит недопустимые символы."
        if re.match(r"^[-a-zA-Z0-9_]+$", slug) is None:
            raise serializers.ValidationError(slug + text)


def validate_tags(data):
    if not data:
        raise serializers.ValidationError({"tags": ["Обязательное поле."]})
    if len(data) != len(set(data)):
        raise serializers.ValidationError(
            {"tags": ["Выбранные теги не должны повторяться."]}
        )
    if len(data) < 1:
        raise serializers.ValidationError(
            {"tags": ["Хотя бы один тэг должен быть указан."]}
        )
    for tag in data:
        if not Tag.objects.filter(id=tag).exists():
            raise serializers.ValidationError(
                {"tags": ["Тэг отсутствует в БД."]}
            )
    return data


def validate_ingredients(data):
    if not data:
        raise serializers.ValidationError(
            {"ingredients": ["Обязательное поле."]}
        )
    return data