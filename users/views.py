from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserSerializer, UserProfileSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import Profile
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate


class CreateUserAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=data.get('username'), 
                password=data.get('password'), 
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
                )
            profile_data = {
                'user': user.id,
                'profile_type': data.get('profile_type'),
                'phone_number': data.get('phone_number')
            }
            profile_serializer = UserProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                response_data = {
                    'user': serializer.data,
                    'profile': profile_serializer.data
                }
                return Response({"success": True, 'data': response_data}, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllUsersAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        users = User.objects.all()
        usernames = [user['username'] for user in UserSerializer(users, many=True).data]
        return Response({"success": True, 'data': usernames})
     

class GetTokenForUserAPIView(APIView):
    
    def post(self, request):
        data = request.data
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            return Response({"success": False, 'msg': 'Invalid password or username'})
        
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        access_token.payload['user_id'] = user.id
        access_token.payload['username'] = user.get_username()
        access_token.payload['profile_type'] = user.profile.profile_type
        
        response = {
            'access': str(access_token),
            'refresh': str(refresh_token)
        }
        return Response({"success": True, 'tokens': response})


class UserProfileTypesAPIView(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        profile_types = [profile_data['profile_type'] for profile_data in serializer.data]
        return Response({'success': True, 'profile_types': profile_types})
    

class UserFullNameAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        full_name = []
        for user in users:
            full_name.append({
                'first_name': user.first_name,
                'last_name': user.last_name,
            })
        if full_name == None:
            return Response({'success': True, 'detail': 'User Full Name doesn’t exist'})
        return Response({'success': True, 'full_name': full_name})


class LogoutAPIView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)