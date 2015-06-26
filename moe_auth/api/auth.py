from moe_auth.auth.views import Login as BaseLogin
from moe_auth.auth.serializers import UserDetailSerializer

class Login(BaseLogin):
    response_serializer = UserDetailSerializer