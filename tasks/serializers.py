# # from rest_framework import serializers
# from django.contrib.auth.models import User
# from .models import Task

# # Basic serializer class to replace DRF serializer
# class TaskSerializer:
#     def __init__(self, instance=None, data=None, **kwargs):
#         self.instance = instance
#         self.data = data
#         self.validated_data = {}
#         self.errors = {}
        
#     def is_valid(self):
#         # Basic validation - in a real app, add more validation here
#         self.validated_data = {}
#         self.errors = {}
        
#         # Field validation
#         if self.data:
#             # Required fields
#             if not self.data.get('title', '').strip():
#                 self.errors['title'] = ['Title is required']
                
#             # Copy valid data
#             for field in ['title', 'description', 'date', 'status']:
#                 if field in self.data and self.data[field]:
#                     self.validated_data[field] = self.data[field]
                    
#         return not self.errors
    
#     def save(self, **kwargs):
#         # Update instance with validated data and kwargs
#         if self.instance:
#             # Update existing instance
#             for key, value in self.validated_data.items():
#                 setattr(self.instance, key, value)
            
#             # Set any additional attributes from kwargs
#             for key, value in kwargs.items():
#                 setattr(self.instance, key, value)
                
#             self.instance.save()
#             return self.instance
#         else:
#             # Create new instance
#             instance = Task.objects.create(**self.validated_data, **kwargs)
#             return instance

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email']
#         read_only_fields = ['id']

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'password2']
    
#     def validate(self, data):
#         if data['password'] != data['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return data
    
#     def create(self, validated_data):
#         validated_data.pop('password2')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data.get('email', ''),
#             password=validated_data['password']
#         )
#         return user