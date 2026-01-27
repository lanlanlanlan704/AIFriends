from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class RefreshTokenView(APIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response({
                    'result':'refresh token not found',
                }, status=401) # 必须加401
            refresh = RefreshToken(refresh_token) # 如果refresh token过期会报异常
            if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKEN']:
                refresh.set_jti()
                response = Response({
                    'result':'refresh token is valid',
                    'access':str(refresh.access_token),
                })
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    max_age=86400 * 7,
                    samesite='Lax',
                    secure=True,
                )
                return response
            return Response({
                'result':'refresh token is invalid',
                'access':str(refresh.access_token),
            })
        except:
            return Response({
                'result' :'refresh token过期了'
            },status=401) #  必须加401