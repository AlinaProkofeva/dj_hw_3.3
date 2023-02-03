from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""


    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        '''Проверка количества открытых объявлений перед созданием'''

        open_advs_quantity = self.context["request"].user.advertisement_set.filter(status='OPEN')
        if len(open_advs_quantity) >= 8:
            raise ValidationError('У пользователя не может быть больше 8 открытых объявлений!')

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # TODO: добавьте требуемую валидацию

        '''Проверка количества открытых объявлений + запроса замены статуса перед изменением: 
        проверка обхода ограничения на количество объявлений'''

        open_advs_quantity = self.context["request"].user.advertisement_set.filter(status='OPEN')

        if "status" in data and data["status"] == "OPEN" and len(open_advs_quantity) >= 8:
            raise ValidationError('У пользователя не может быть больше 8 открытых объявлений!')

        return data
