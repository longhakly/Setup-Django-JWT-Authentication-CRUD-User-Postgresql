from django.shortcuts import  render, redirect
from .forms import NewUserForm
from .models import UserProfile, Role, User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import json
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.exceptions import TokenError
from .function import create_profile
def home(request):
	return render(request,'home.html',{})

@api_view(['POST'])
def register_request(request):
	if request.method == "POST":
		data = json.loads(request.body)

		check_user = User.objects.filter(email = data.get('email'))
		if check_user:
			return JsonResponse({'status': HttpResponse.status_code, 'message': 'A User already exists with this email'})	
				
		user = User.objects.create_user(
			first_name = data.get('first_name'),
			last_name= data.get('last_name'),
			birthday = data.get('birthday'),
			phone_number = data.get('phone_number'),
			email = data.get('email'),
			password = data.get('password')
			)
		user.role = Role.objects.get(id =1)
		user.save()
		create_profile(user.id)
		return JsonResponse({'status': HttpResponse.status_code,  'message': 'Successfully created user'})
	else:
		return JsonResponse({'status': HttpResponse.status_code, 'message': 'Invalid request method'})

@api_view(['POST'])
def login_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is None:
            raise exceptions.AuthenticationFailed('Invalid email or password')
        # login(request, user)
	    
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
	    
        response = JsonResponse({'token': access_token})
        response.set_cookie(key='refreshToken', value=refresh_token, httponly=True)
        return response
	
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_request(request):
    try:
        refresh_token = request.COOKIES.get('refreshToken')

        # Blacklist refresh token
        rf_token = RefreshToken(refresh_token)
        rf_token.blacklist()

        response = JsonResponse({'message': 'Successfully logged out.'}, status=200)
        response.delete_cookie(key='refreshToken')
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.COOKIES.get('refreshToken')

    if not refresh_token:
        raise TokenError('Refresh token is missing')

    try:
        token = RefreshToken(refresh_token)
        access_token = str(token.access_token)

        # Set the new refresh token as a cookie
        response = JsonResponse({'accessToken': access_token}, status=200) 
        response.set_cookie(key='refreshToken', value=str(token), httponly=True)
        return response

    except TokenError as e:
        raise TokenError(str(e))
    
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password_reset.html", context={"password_reset_form":password_reset_form})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
	get_current_user = request.user
	if get_current_user.role.name == "ADMIN":
		users = User.objects.all()
		list_users = []
		for user in users:
			json_user = {
				"id" : user.id,
				"first_name": user.first_name,
				"last_name": user.last_name,
				"username": f"{user.first_name} {user.last_name}",
				"email": user.email,
				"role": user.role.name
			}
			list_users.append(json_user)
		print(list_users)
		return JsonResponse({'status': status.HTTP_200_OK,  'data': list_users})
	else:
		return JsonResponse({'status': status.HTTP_401_UNAUTHORIZED, 'message': 'Unauthorized'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
	user = request.user
	list_users = []
	json_user = {
				"id" : user.id,
				"first_name": user.first_name,
				"last_name": user.last_name,
				"username": f"{user.first_name} {user.last_name}",
				"phone_number": user.phone_number,
				"email": user.email,
				"role" : user.role.name,
				"city": user.profile.city,
				"location": user.profile.location,
				"profile_pics": user.profile.profile_picture.url
		}
	list_users.append(json_user)
	return JsonResponse(list_users, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_only_user(request, user_id):
    get_current_user = request.user
    if get_current_user.role.name == "ADMIN":
        user = User.objects.filter(id=user_id).first()
        list_users = []
        json_user = {
					"id" : user.id,
					"first_name": user.first_name,
					"last_name": user.last_name,
					"username": f"{user.first_name} {user.last_name}",
					"phone_number": user.phone_number,
					"email": user.email,
					"role" : user.role.name
			}
        list_users.append(json_user)
        return JsonResponse({'status': status.HTTP_200_OK,  'data': list_users})
    else:
        return JsonResponse({'status': status.HTTP_401_UNAUTHORIZED, 'message': 'Unauthorized'})

def profile_request(request, user_id):
	if request.method == "GET":
		# user_id = request.GET.get('user_id')
		try:
			check_user = User.objects.get(id= int(user_id))
			try :
				check_profile = UserProfile.objects.get(user = check_user)
				user_data = {
					"id" : check_profile.id,
					"first_name": check_profile.user.first_name,
					"last_name": check_profile.user.last_name,
					"username" : f"{check_profile.user.first_name} {check_profile.user.last_name}",
					"address" : check_profile.location,
					"city" : check_profile.city,
					"role" : check_user.role.name,
					"number": check_user.phone_number
				}
				return JsonResponse(user_data)
			except UserProfile.DoesNotExist:
				return JsonResponse({"status": "User Profile doesn't exist"})
		except User.DoesNotExist:
			return JsonResponse({"status": "User doesn't exist"})
	else:
		data = json.loads(request.body)
		location = data["location"]
		first_name = data["first_name"]
		last_name = data["last_name"]
		city = data["city"]
		
		try:
			check_user = User.objects.get(id = int(user_id))	
			try:
				check_profile = UserProfile.objects.get(user = check_user)
				check_profile.location = location
				check_profile.city = city
				check_profile.user.first_name = first_name
				check_profile.user.last_name = last_name
				check_profile.save()
				return JsonResponse({"status": "User Profile has updated"})
			except UserProfile.DoesNotExist:
				return JsonResponse({"status": "User Profile doesn't exist"})
		except User.DoesNotExist:
			return JsonResponse({"status": "Can't Update User Profile, Because User does not exist"})
 
def update_profile_image(request, user_id):
	user = User.objects.get(id = user_id)
	user_profile = UserProfile.objects.get(user = user)
	if request.method == 'POST':
		image = request.FILES.get('image')
		if image:
			fs = FileSystemStorage(location='media/profile_pics/')
			filename = fs.save(image.name, image)
			image_url = f"profile_pics/{filename}"
		else:
			image_url = None
		user_profile.profile_picture = image_url
		user_profile.save()
		return JsonResponse({'message': 'Profile image updated successfully.'})
	return JsonResponse({'message': 'Invalid request method.'})
	
# def create_profile(request):
# 	if request.method == "POST":
# 		user_id = request.POST.get("user_id")
# 		location = request.POST.get("location")
# 		city = request.POST.get("city")
# 		try:
# 			check_user = User.objects.get(id = int(user_id))	
# 			try:
# 				check_profile = UserProfile.objects.get(user = check_user)
# 				return JsonResponse({"status": f"User {check_profile.user.username} Profile is already exist"})
# 			except UserProfile.DoesNotExist:
# 				create_profile = UserProfile(user=check_user, location = location, city = city)
# 				create_profile.save()
# 				return JsonResponse({"status": "Created User Profile"})
# 		except User.DoesNotExist:
# 			return JsonResponse({"status": "Can't Create User Profile, Because User does not exist"})
# 	return HttpResponse(status=405)

def get_role(request):
	roles = Role.objects.all()
	list_roles = []
	for role in roles:
		json_role = {
			"id": role.id,
			"name": role.name
		}
		list_roles.append(json_role)
	return JsonResponse(list_roles, safe=False)

def test(request):
	user = User.objects.get(id = 6)
	a =  Role.objects.filter(users=user.id).first()
	print(a)


	return False