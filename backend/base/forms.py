from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Role, User


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)
	class Meta:
		model = User
		fields = ("first_name", "last_name", "phone_number", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		assign_role_user = Role.objects.get(id =1)
		user.role = assign_role_user
		if commit:
			user.save()
		return user