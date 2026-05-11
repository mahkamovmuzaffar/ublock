import json
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from .models import User

logger = logging.getLogger(__name__)
# TODO: Add more granular logging throughout the views for better observability and debugging.

class UserRegisterView(View):
    """
    Register a new user account.
    Accepts username, email, password, and optional name fields.
    """
    def post(self, request):
        try:
            # Parse incoming JSON body
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()

            # Ensure all required fields are present
            if not username or not email or not password:
                return JsonResponse({
                    'success': False,
                    'error': 'username, email, and password are required'
                }, status=400)

            # Reject duplicate username
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Username already taken'
                }, status=400)

            # Reject duplicate email
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email already registered'
                }, status=400)

            # Create the user with a hashed password
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            # Return the new user's public data
            return JsonResponse({
                'success': True,
                'message': 'Account created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception:
            logger.exception('Failed to register user')
            return JsonResponse({'success': False, 'error': 'Failed to create account'}, status=500)


class UserLoginView(View):
    """
    Authenticate a user and start a session.
    Accepts username and password.
    """
    def post(self, request):
        try:
            # Parse incoming JSON body
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')

            # Ensure credentials are provided
            if not username or not password:
                return JsonResponse({
                    'success': False,
                    'error': 'Username and password are required'
                }, status=400)

            # Verify credentials against the database
            user = authenticate(request, username=username, password=password)

            # Reject invalid credentials
            if not user:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid credentials'
                }, status=401)

            # Reject disabled accounts
            if not user.is_active:
                return JsonResponse({
                    'success': False,
                    'error': 'Account is disabled'
                }, status=403)

            # Create a session for the authenticated user
            login(request, user)

            # Return user profile data on successful login
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_kyc_verified': user.is_kyc_verified,
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception:
            logger.exception('Login failed')
            return JsonResponse({'success': False, 'error': 'Login failed'}, status=500)


class UserLogoutView(LoginRequiredMixin, View):
    """
    End the current user session.
    """
    def post(self, request):
        # Flush the session and clear the auth cookie
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logged out successfully'})


class UserProfileView(LoginRequiredMixin, View):
    """
    GET  — return the authenticated user's profile.
    PUT  — update allowed profile fields (name, email, bio, phone_number).
    """
    def get(self, request):
        # Read the user object attached to the current session
        user = request.user

        # Return all public and account-level fields
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'bio': user.bio,
                'phone_number': user.phone_number,
                'is_kyc_verified': user.is_kyc_verified,
                'date_joined': user.date_joined.isoformat(),
                'updated_at': user.updated_at.isoformat(),
            }
        })

    def put(self, request):
        try:
            # Parse incoming JSON body
            data = json.loads(request.body)
            user = request.user

            # Apply any provided fields that are safe to update directly
            for field in ('first_name', 'last_name', 'bio', 'phone_number'):
                if field in data:
                    setattr(user, field, data[field])

            # Email needs a uniqueness check before applying
            if 'email' in data:
                new_email = data['email'].strip()
                if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Email already in use'
                    }, status=400)
                user.email = new_email

            # Persist all changes in a single write
            user.save()

            # Return the updated profile
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'bio': user.bio,
                    'phone_number': user.phone_number,
                    'is_kyc_verified': user.is_kyc_verified,
                    'date_joined': user.date_joined.isoformat(),
                    'updated_at': user.updated_at.isoformat(),
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception:
            logger.exception('Failed to update profile for user %s', request.user.id)
            return JsonResponse({'success': False, 'error': 'Failed to update profile'}, status=500)


class UserChangePasswordView(LoginRequiredMixin, View):
    """
    Change the authenticated user's password.
    Requires current_password, new_password, and confirm_password.
    """
    def post(self, request):
        try:
            # Parse incoming JSON body
            data = json.loads(request.body)
            current_password = data.get('current_password', '')
            new_password = data.get('new_password', '')
            confirm_password = data.get('confirm_password', '')

            # Ensure all three fields are present
            if not current_password or not new_password or not confirm_password:
                return JsonResponse({
                    'success': False,
                    'error': 'current_password, new_password, and confirm_password are required'
                }, status=400)

            # Confirm the two new-password fields match
            if new_password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'error': 'New passwords do not match'
                }, status=400)

            # Verify the current password is correct before allowing the change
            if not request.user.check_password(current_password):
                return JsonResponse({
                    'success': False,
                    'error': 'Current password is incorrect'
                }, status=401)

            # Enforce minimum password length
            if len(new_password) < 8:
                return JsonResponse({
                    'success': False,
                    'error': 'New password must be at least 8 characters'
                }, status=400)

            # Hash and save the new password
            request.user.set_password(new_password)
            request.user.save()

            # Re-authenticate so the session stays alive after the password hash changes
            user = authenticate(request, username=request.user.username, password=new_password)
            if user:
                login(request, user)

            return JsonResponse({'success': True, 'message': 'Password changed successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception:
            logger.exception('Failed to change password for user %s', request.user.id)
            return JsonResponse({'success': False, 'error': 'Failed to change password'}, status=500)
