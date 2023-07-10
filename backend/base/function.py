from .models import UserProfile, Role, User
from django.http import JsonResponse
from django.http import HttpResponse

def create_profile(user_id):
	user_id = user_id
	location = ""
	city = ""
	try:
		check_user = User.objects.get(id = int(user_id))	
		try:
			check_profile = UserProfile.objects.get(user = check_user)
			return JsonResponse({"status": f"User {check_profile.user.username} Profile is already exist"})
		except UserProfile.DoesNotExist:
			create_profile = UserProfile(user=check_user, location = location, city = city)
			create_profile.save()
			return JsonResponse({"status": "Created User Profile"})
	except User.DoesNotExist:
		return JsonResponse({"status": "Can't Create User Profile, Because User does not exist"})