from django.shortcuts import render
from rest_framework import generics, mixins
from .models import User
from django.db.models import Q
from .serializers import UserSerializer
from rest_framework.response import Response
from .responses import response
from .serializers import (
    LoginSerializer, ForgotPasswordSerialzier,
        ResetPassWordSerializer, ChangePassWordSerializer
    ) 
from django.core.mail import EmailMessage
from rest_framework.generics import RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

# Create your views here.
import pdb

class UserRudAPIView(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_queryset(self):
        return User.objects.all()

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

class UserCreateAPIView(mixins.CreateModelMixin, generics.ListAPIView):

    lookup_field = 'pk'
    queryset = User.objects.all()
    serializer_class = UserSerializer
   
    def get_queryset(self):
        return User.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        return Response({'message': response['user']['login'], 'user':serializer.data}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    """ Forgot password view class """

    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerialzier

    def post(self, request):
        """ create user using following logic. """

        try:            
            user = User()
            user = user.get_user_by_email(request.data.get('email'))
            token = uuid.uuid4().hex
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            instance = UserVerification()
            instance.create(user.id, token)
            result = Response(
                {'message': response['user']['reset_password'], 'token': token},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            result = Response({"message": e}, status=400)

        return result


class ResetPasswordView(APIView):
    """ Reset password view class """

    serializer_class = ResetPassWordSerializer

    def post(self, request, token):
        try:
            instance = UserVerification()
            user_verify_obj = instance.check_token(token)
            
            if not user_verify_obj:
                raise ValidationError('Token is not valid')
            
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = User()
            user = user.get_user(user_verify_obj.user_id)
            user.set_password(request.data.get('password'))
            user.save()
            user_verify_obj.delete()
            result = Response({'message': response['user']['change_password']})
        except ValidationError as e:
            result = Response({"message": e}, status=400)
       
        return result


class ChangePasswordAPIView(UpdateAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePassWordSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        
        try:
            user_obj = request.user
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if not user_obj.check_password(serializer.data.get("old_password")):
                    raise ValidationError(response['error']['incorrect_password'])
            user_obj.set_password(serializer.data.get("new_password"))
            user_obj.save()
            result = Response({"message": response['user']['change_password']},
                status=status.HTTP_200_OK)
        except ValidationError as e:
            result = Response({"message": e}, status=400)
        return result
