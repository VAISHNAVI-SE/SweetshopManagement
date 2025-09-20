from rest_framework import serializers
from .models import Sweet, Purchase
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class SweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sweet
        fields = ['id', 'name', 'category', 'price', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    sweet = serializers.PrimaryKeyRelatedField(queryset=Sweet.objects.all())

    class Meta:
        model = Purchase
        fields = ['id', 'sweet', 'user', 'quantity', 'purchased_at']
        read_only_fields = ['id', 'user', 'purchased_at']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        user = User.objects.create_user(username=username, password=password)
        return user
