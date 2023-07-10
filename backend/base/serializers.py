# from rest_framework import serializers
# from .models import User, UserProfile, ShopProfile

# class UserProfileSerializer(serializers.ModelSerializer):
#     role = serializers.SerializerMethodField()
#     products = ProductSerializer(many=True, read_only=True)
#     class Meta:
#         model = User
#         fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'products']

#     def get_role(self, obj):
#         return obj.groups.all()[0].name