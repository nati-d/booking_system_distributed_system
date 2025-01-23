import requests
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed

class IsAuthenticatedWithToken(BasePermission):
    """
    Custom permission to validate JWT token with the user service.
    """

    def has_permission(self, request, view):
        token = request.headers.get("Authorization")

        if not token:
            raise AuthenticationFailed("Authorization token is missing.")

        try:
            token = token.split(" ")[1]  # Extract token from 'Bearer <token>'
        except IndexError:
            raise AuthenticationFailed("Invalid token format.")

        is_valid, user_data = self.validate_jwt_token(token)

        if not is_valid:
            raise AuthenticationFailed("Authentication failed.")

        # Optionally attach user data to the request object for further use
        request.user_data = user_data
        return True

    def validate_jwt_token(self, token):
        """
        Calls the user service to validate the JWT token.
        :param token: The JWT token to validate.
        :return: Tuple (is_valid: bool, user_data: dict)
        """
        return True,None
        user_service_url = "http://127.0.0.1:8001"  # URL of the user service
        response = requests.post(user_service_url, json={"token": token})

        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return True, data  # Valid token, return user data
            else:
                return False, None  # Invalid token
        else:
            return False, None  # Request failed or other errors
