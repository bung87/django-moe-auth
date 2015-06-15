from moe.auth.views import Login as BaseLogin
from moe.auth.serializers import UserDetailSerializer

class Login(BaseLogin):
    response_serializer = UserDetailSerializer