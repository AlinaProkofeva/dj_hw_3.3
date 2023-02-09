from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, Favourites
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
        if len(open_advs_quantity) >= 10:
            raise ValidationError('У пользователя не может быть больше 10 открытых объявлений!')

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        '''Проверка количества открытых объявлений + запроса замены статуса перед изменением: 
        проверка обхода ограничения на количество объявлений'''

        open_advs_quantity = self.context["request"].user.advertisement_set.filter(status='OPEN')

        if "status" in data and data["status"] == "OPEN" and len(open_advs_quantity) >= 10:
            raise ValidationError('У пользователя не может быть больше 10 открытых объявлений!')

        return data


class FavouritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourites
        fields = ['id', 'advertisement']

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user

        '''Проверка на добавление владельцем'''
        if self.context["request"].user == validated_data["advertisement"].creator:
            raise ValidationError('Нельзя добавить в избранное собственное объявление!')

        '''Проверка на дублирование объявления в избранное'''
        id_to_add = validated_data["advertisement"].id
        advs_with_this_id_in_base = self.context["request"].user.favourites_set.filter(advertisement__id=id_to_add)
        if len(advs_with_this_id_in_base) > 0:
            raise ValidationError('Это объявление уже в избранных у пользователя!')

        return super().create(validated_data)




