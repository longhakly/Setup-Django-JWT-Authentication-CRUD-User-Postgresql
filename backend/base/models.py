from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager, Permission
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, last_name = None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), last_name = last_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, last_name, email, password, **extra_fields):
        user = self.create_user(email, password=password, last_name= last_name, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class Role(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)   
    birthday = models.DateField(null=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users', null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name']

    objects = UserManager()
    def has_perm(self, perm, obj=None):
        return self.is_superuser or self.user_permissions.filter(codename=perm).exists()
    def has_module_perms(self, app_label):
        return self.is_superuser or self.user_permissions.filter(content_type__app_label=app_label).exists()
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user =models.OneToOneField(User, on_delete=models.CASCADE , related_name='profile')
    city = models.CharField(max_length=50, null=True)
    location = models.CharField(max_length=255, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.png', blank=True, null=True)

    def __str__(self):
        return self.user.last_name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id}'

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()