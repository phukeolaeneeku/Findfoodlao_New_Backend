import base64
import os
import random
import string

import pytz
from django.db import transaction
from django.http import JsonResponse
from PIL import Image
import io
import requests
from django.core.files.base import ContentFile
import requests
from datetime import datetime

from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
from drf_yasg.utils import swagger_auto_schema
from google.oauth2 import id_token as google_id_token
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from store.models import StoreModel
from store.serializers import (
    OnlyStoreInfoSerializer,
)
from .form import UserForm
from .models import CheckEmail, UserModel
from .serializers import (
    UserSerializer,
    LoginSerializer,
    SellerSerializer,
    PostUserSerializer,
    GetUserSerializer,
    AdminUserSerializer,
    ClientUserSerializer,
    SellerUserSerializer,
    RestaurantSerializer,
    EmployeeSerializer,
)
from django.shortcuts import render
import smtplib
import jwt
from django.conf import settings
from rest_framework import generics, permissions
from restaurant2.models import Restaurant, Employee


# Send email
class SendEmail(APIView):
    @swagger_auto_schema(
        tags=["Email Authentication"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        user_email = request.data.get("email")
        if not user_email:
            return Response(
                {"message": "Please enter your e-mail."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        random_code = "".join(
            random.choices(string.digits, k=6)
        )  # Generate 6-digit random string
        subject = "[HUMASCOT] Membership verification code"
        body = f"Email verification code: {random_code}"  # Add to random code body
        email = EmailMessage(
            subject,
            body,
            to=[user_email],
        )
        email.send()

        # Save authentication code to DB
        code = CheckEmail.objects.create(code=random_code, email=user_email)
        return Response(
            {"message": "Your email has been sent. Please check your mailbox."},
            status=status.HTTP_200_OK,
        )


class CheckEmailView(APIView):
    def post(self, request):
        # # Most recent authentication code instance
        # code_obj = (
        # CheckEmail.objects.filter(email=email).order_by("-created_at").first()
        # )
        # # Check after deployment
        code = request.data.get("code")
        email = request.data.get("email")
        code_obj = CheckEmail.objects.filter(email=email, code=code).first()
        if code_obj is None:
            return Response(
                {"message": "No verification code was sent to that email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tz = pytz.timezone("Asia/Vientiane")

        # If the authentication code has expired
        if code_obj.expires_at < datetime.now(tz=tz):
            code_obj.delete()
            return Response(
                {"message": "The verification code has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code_obj.delete()  # Delete email verification code
        return Response(
            {"message": "Email verification has been completed.", "is_checked": True},
            status=status.HTTP_200_OK,
        )


# join the membership
class SignupView(APIView):
    # def get(self, request):
    #     user = request.user.is_authenticated
    #     if user:
    #         return redirect("/")
    #     else:
    #         param = request.GET.get("user_type")  # Parameter called ‘param_name’
    #         if not param:
    #             return render(
    #                 request,
    #                 "user/user_type_choice.html",
    #             )
    #         elif str(param) == "1":
    #             return render(
    #                 request,
    #                 "user/basic_signup.html",
    #             )
    #         elif str(param) == "2":
    #             return render(
    #                 request,
    #                 "user/seller_signup.html",
    #             )

    @swagger_auto_schema(
        tags=["join the membership"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        with transaction.atomic():
            category = request.data.get("category")
            email = request.data.get("email")
            code = request.data.get("code")
            password = request.data.get("password")
            password2 = request.data.get("password2")
            profile_image = request.data.get("profile_image")
            code_obj = CheckEmail.objects.filter(email=email, code=code).first()

            # Check whether the password and password match
            if password != password2:
                return JsonResponse(
                    {
                        "message": "Your password and password confirmation do not match."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check for email duplicates
            user = UserModel.objects.filter(email=email)
            if user.exists():
                return Response(
                    {"message": "The email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if code_obj is None:
                return Response(
                    {"message": "No verification code was sent to that email."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tz = pytz.timezone("Asia/Vientiane")

            # If the verification code has expired
            if code_obj.expires_at < datetime.now(tz=tz):
                code_obj.delete()
                return Response(
                    {"message": "The verification code has expired."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if your email matches

            if profile_image == "undefined" or profile_image is None:
                # If the image comes as an empty value, use copy to change it!
                # deepcopy -> Import copy module? -> Complete copy! (safe)
                # Consider using try, except -> Additional exception handling!
                data = request.data.copy()
                data["profile_image"] = None
                serializer = UserSerializer(data=data)
            else:
                serializer = UserSerializer(data=request.data)
                
            # if serializer.is_valid():
            #     """
            #     Add store-specific membership registration logic
            #     """
            #     if category != "2":
            #         code_obj.delete()  # Delete email verification code
            #         serializer.save()
            #     if category == "2":
            #         name = request.data.get("name")
            #         address = request.data.get("address")
            #         if not name or not address:
            #             return Response(
            #                 {"message": "Please enter all required information."},
            #                 status.HTTP_400_BAD_REQUEST,
            #             )
            #         sell_serializer = SellerSerializer(data=request.data)
            #         code_obj.delete()  # Delete email verification code
            #         if sell_serializer.is_valid():
            #             serializer.save(is_seller=True)
            #             sell_serializer.save(seller_id=serializer.data.get("id"))
            #         else:
            #             return Response(
            #                 {"message": f"{serializer.errors}"},
            #                 status=status.HTTP_400_BAD_REQUEST,
            #             )
        
            #     return Response(
            #         {"message": "Your registration has been completed."},
            #         status=status.HTTP_201_CREATED,
            #     )
            # else:
            #     return Response(
            #         {"message": f"{serializer.errors}"},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )
            
            if serializer.is_valid():
                """
                Add store-specific membership registration logic
                """
                if category != "2":
                    code_obj.delete()  # Delete email verification code
                    serializer.save()
                if category == "2":
                    name = request.data.get("name")
                    address = request.data.get("address")
                    if not name or not address:
                        return Response(
                            {"message": "Please enter all required information."},
                            status.HTTP_400_BAD_REQUEST,
                        )
                    restaurant_serializer = RestaurantSerializer(data=request.data)
                    code_obj.delete()  # Delete email verification code
                    if restaurant_serializer.is_valid():
                        serializer.save(is_restaurant=True)
                        restaurant_serializer.save(restaurant_id=serializer.data.get("id"))
                    else:
                        return Response(
                            {"message": f"{serializer.errors}"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
        
                return Response(
                    {"message": "Your registration has been completed."},
                    status=status.HTTP_201_CREATED,
                )

                return Response(
                    {"message": "Your registration has been completed."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": f"{serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class RestaurantSignupView(APIView):
    @swagger_auto_schema(
        tags=["join the membership"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        with transaction.atomic():
            email = request.data.get("email")
            password = request.data.get("password")
            password2 = request.data.get("password2")
            profile_image = request.data.get("profile_image")

            # Check whether the password and password match
            if password != password2:
                return JsonResponse(
                    {
                        "message": "Your password and password confirmation do not match."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check for email duplicates
            user = UserModel.objects.filter(email=email)
            if user.exists():
                return Response(
                    {"message": "The email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if profile_image == "undefined" or profile_image is None:
                # If the image comes as an empty value, use copy to change it!
                # deepcopy -> Import copy module? -> Complete copy! (safe)
                # Consider using try, except -> Additional exception handling!
                data = request.data.copy()
                data["profile_image"] = None
                serializer = UserSerializer(data=data)
            else:
                serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                name = request.data.get("name")
                address = request.data.get("address")
                if not name or not address:
                    return Response(
                        {"message": "Please enter all required information."},
                        status.HTTP_400_BAD_REQUEST,
                    )
                restaurant_serializer = RestaurantSerializer(data=request.data)
                if restaurant_serializer.is_valid():
                    serializer.save(is_restaurant=True)
                    restaurant_serializer.save(restaurant_id=serializer.data.get("id"))
                else:
                    return Response(
                        {"message": f"{serializer.errors}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                return Response(
                    {"message": "Your registration has been completed."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": f"{serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class RestaurantLoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response(data={"message": "Email does not exist."}, status=400)

        if not check_password(password, user.password):
            return Response(data={"message": "Incorrect password."}, status=400)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            token = serializer.validated_data
            is_admin = user.is_admin
            is_restaurant = user.is_restaurant
            restaurant = Restaurant.objects.filter(
                restaurant=user
            ).first()  # Use .first() to get the first object.
            restaurant_id = restaurant.id if restaurant else False
            origin_restaurant_name = restaurant.name if restaurant else False

            if is_restaurant == True:
                return Response(
                    data={
                        "token": token,
                        "user_id": user.id,
                        "is_admin": is_admin,
                        "is_restaurant": is_restaurant,
                        "restaurant_id": restaurant_id,
                        "user_name": user.nickname,
                        "origin_restaurant_name": origin_restaurant_name,
                        "email": user.email if user.email else False,
                        "image": (
                            user.profile_image.url if user.profile_image else False
                        ),
                    },
                    status=200,
                )
            else:
                return Response(
                    data={"message": "Your account is not the Restaurant owner!"},
                    status=400,
                )

        else:
            return Response(
                data={
                    "message": "An error occurred. Please contact the administrator."
                },
                status=400,
            )


# Employee
class EmployeeSignupView(APIView):
    @swagger_auto_schema(
        tags=["join the membership"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        with transaction.atomic():
            email = request.data.get("email")
            password = request.data.get("password")
            password2 = request.data.get("password2")
            profile_image = request.data.get("profile_image")

            # Check whether the password and password match
            if password != password2:
                return JsonResponse(
                    {
                        "message": "Your password and password confirmation do not match."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check for email duplicates
            user = UserModel.objects.filter(email=email)
            if user.exists():
                return Response(
                    {"message": "The email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if profile_image == "undefined" or profile_image is None:
                # If the image comes as an empty value, use copy to change it!
                # deepcopy -> Import copy module? -> Complete copy! (safe)
                # Consider using try, except -> Additional exception handling!
                data = request.data.copy()
                data["profile_image"] = None
                serializer = UserSerializer(data=data)
            else:
                serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                phone = request.data.get("phone")
                address = request.data.get("address")
                if not phone or not address:
                    return Response(
                        {"message": "Please enter all required information."},
                        status.HTTP_400_BAD_REQUEST,
                    )
                employee_serializer = EmployeeSerializer(data=request.data)
                if employee_serializer.is_valid():
                    serializer.save(is_employee_of_restaurant=True)
                    employee_serializer.save(employee_id=serializer.data.get("id"))
                else:
                    return Response(
                        {"message": f"{serializer.errors}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                return Response(
                    {"message": "Your registration has been completed."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": f"{serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class EmployeeLoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        restaurant_id = data.get("restaurant")
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response(data={"message": "Invalid credentials."}, status=400)

        if not user.check_password(password):
            return Response(data={"message": "Invalid credentials."}, status=400)

        try:
            employee = Employee.objects.get(employee=user, restaurant_id=restaurant_id)
        except Employee.DoesNotExist:
            return Response(data={"message": "No employee record found for this restaurant."}, status=400)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['access']

        return Response(
            data={
                "token": token,
                "user_id": user.id,
                "user_name": user.nickname,
                "is_employee": True,
                "employee_id": employee.id,
                "email": user.email,
                "image": user.profile_image.url if user.profile_image else None,
            },
            status=200,
        )


# ===== Manage Admin user =====
class CreateSuperuserView(APIView):
    serializer_class = UserSerializer

    def post(self, request, format=None):
        email = request.data.get("email")
        # Check for email duplicates
        user = UserModel.objects.filter(email=email)
        if user.exists():
            return Response(
                {"message": "The email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save(is_admin=True, is_seller=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListAdminUsersView(APIView):
    serializer_class = AdminUserSerializer

    def get(self, request, format=None):
        admin_users = UserModel.objects.filter(is_admin=True).order_by("-id")
        serializer = self.serializer_class(admin_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAdminUserByIdView(APIView):
    serializer_class = AdminUserSerializer

    def get(self, request, user_id, format=None):
        try:
            user = UserModel.objects.get(id=user_id, is_admin=True)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DeleteAdminUserView(APIView):
    serializer_class = AdminUserSerializer

    def delete(self, request, user_id, format=None):
        try:
            user = UserModel.objects.get(id=user_id, is_admin=True)
            user.delete()
            return Response(
                {"message": "Admin user deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UpdateAdminUserView(APIView):
    serializer_class = AdminUserSerializer

    def put(self, request, user_id, format=None):
        try:
            user = UserModel.objects.get(id=user_id, is_admin=True)
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===== Manage Admin user =====
class ListClientUsersView(APIView):
    serializer_class = ClientUserSerializer

    def get(self, request, format=None):
        user = UserModel.objects.filter(
            is_active=True, is_admin=False, is_seller=False
        ).order_by("-id")
        serializer = self.serializer_class(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetClientUserByIdView(APIView):
    serializer_class = ClientUserSerializer

    def get(self, request, user_id, format=None):
        try:
            user = UserModel.objects.get(id=user_id, is_active=True)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Client user not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DeleteClientUserView(APIView):
    serializer_class = ClientUserSerializer

    def delete(self, request, user_id, format=None):
        try:
            user = UserModel.objects.get(id=user_id, is_active=True)
            user.delete()
            return Response(
                {"message": "Client user deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Client user not found"}, status=status.HTTP_404_NOT_FOUND
            )


class ListSellerUsersView(APIView):
    serializer_class = SellerUserSerializer

    def get(self, request, format=None):
        user = UserModel.objects.filter(
            is_active=True, is_admin=False, is_seller=True
        ).order_by("-id")
        serializer = self.serializer_class(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetSellerUserByIdView(APIView):
    serializer_class = SellerUserSerializer

    def get(self, request, user_id, format=None):
        try:
            user = UserModel.objects.get(id=user_id, is_seller=True)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Seller user not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DeleteSellerUserView(APIView):
    serializer_class = SellerUserSerializer

    def delete(self, request, user_id, format=None):
        try:
            user = UserModel.objects.get(id=user_id, is_seller=True)
            user.delete()
            return Response(
                {"message": "Seller user deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Seller not found"}, status=status.HTTP_404_NOT_FOUND
            )


# log in
class LoginView(TokenObtainPairView):
    # template_name = "user/signin.html"  # Template for login page
    # form_class = UserForm
    # serializer_class = LoginSerializer

    # def get(self, request, *args, **kwargs):
    #     return render(
    #         request,
    #         self.template_name,
    #     )

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response(data={"message": "Email does not exist."}, status=400)

        if not check_password(password, user.password):
            return Response(data={"message": "Incorrect password."}, status=400)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            token = serializer.validated_data
            is_admin = user.is_admin
            store = StoreModel.objects.filter(
                seller=user
            ).first()  # Use .first() to get the first object.
            store_id = store.id if store else False
            origin_store_name = store.name if store else False
            
            restaurant = Restaurant.objects.filter(
                restaurant=user
            ).first() 
            restaurant_id = restaurant.id if restaurant else False
            restaurnt_name = restaurant.name if restaurant else False
            
            employee = Employee.objects.filter(
                employee=user
            ).first() 
            employee_id = employee.id if employee else False
            employee_role = employee.role if employee else False
            
            return Response(
                data={
                    "token": token,
                    "user_id": user.id,
                    "is_admin": is_admin,
                    "store_id": store_id,
                    "user_name": user.nickname,
                    "origin_store_name": origin_store_name,
                    "email": user.email if user.email else False,
                    "image": user.profile_image.url if user.profile_image else False,
                    "restaurant_id": restaurant_id,
                    "restaurnt_name": restaurnt_name,
                    "employee_id": employee_id,
                    "employee_role": employee_role
                },
                status=200,
            )
        else:
            return Response(
                data={
                    "message": "An error occurred. Please contact the administrator."
                },
                status=400,
            )


# User-related logic
class UserView(APIView):
    def get(self, request):
        user = get_object_or_404(UserModel, email=request.user)
        data = {}
        if user.is_seller:
            store = user.storemodel_set.all().first()
            data["store_info"] = OnlyStoreInfoSerializer(store).data

        data["user_info"] = GetUserSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Password change and withdrawal"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        """
        <Reset password>
         Reset password if lost
        """
        email = request.data.get("email")
        password = request.data.get("password")
        password2 = request.data.get("password2")
        code = request.data.get("code")
        code_obj = CheckEmail.objects.filter(email=email, code=code).first()
        if code_obj is None:
            return Response(
                {"message": "No verification code was sent to that email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tz = pytz.timezone("Asia/Vientiane")

        # If the verification code has expired
        if code_obj.expires_at < datetime.now(tz=tz):
            code_obj.delete()
            return Response(
                {"message": "The verification code has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code_obj.delete()  # Delete email verification code

        # Check if your email matches
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response(
                {"message": "Email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password2:
            return Response(
                {"message": "Your passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update password
        user.set_password(password)
        user.save()

        return Response(
            {"message": "Your password has been changed."}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        tags=["Password change and withdrawal"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def patch(self, request):
        """
        <Change password>
         Change password after logging in
        """
        try:
            user = get_object_or_404(UserModel, id=request.user.id)
            origin_password = request.data.get("origin_password")
            new_password = request.data.get("password")
            check_new_password = request.data.get("password2")
            data = request.data.copy()
            image = request.data.get("profile_image")
            # Confirm new password & password match
            # if origin_password == '' or not new_password == '' or not check_new_password == '':
            #     data['password'] = None
            # When changing your password
            if (
                new_password != check_new_password
                or not new_password
                or not check_new_password
            ):
                return Response(
                    {"message": "New password does not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify original password matches
            if not check_password(origin_password, user.password):
                return Response(
                    {"message": "Passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if image == "undefined" or not image:
                data["profile_image"] = None

            if not new_password:
                print(data)
                user.profile_image = data["profile_image"]
                user.save()
                return Response(
                    {
                        "message": "Modifications completed!",
                        "image": (
                            user.profile_image.url if user.profile_image else False
                        ),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                serializer = UserSerializer(user, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    # If you change your password
                    return Response(
                        {
                            "message": "Modifications completed!",
                            "image": (
                                user.profile_image.url if user.profile_image else False
                            ),
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    print(serializer.errors)
                    return Response(
                        {serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                    )

        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Password change and withdrawal"], responses={200: "Success"}
    )
    # Delete member
    def delete(self, request):
        try:
            user = request.user
            user.delete()
            return Response(
                {"message": "I deleted my account."}, status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserProfile(APIView):
    def patch(self, request):
        user = get_object_or_404(UserModel, id=request.user.id)
        image = request.data.get("profile_image")
        data = request.data.copy()

        if image == "undefined" or not image:
            data["profile_image"] = None
        user.profile_image = resize_image(data["profile_image"])
        user.save()
        return Response(
            {
                "message": "Modifications completed!",
                "image": user.profile_image.url if user.profile_image else False,
            },
            status=status.HTTP_200_OK,
        )


# Change to front domain after deployment
URI = "http://127.0.0.1:8000/user/signin"
URI2 = "https://humascot.shop/user/signin"
URI3 = "https://web4all.site/user/signin"
URI4 = "https://web4all.store/user/signin"

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def get_google_credentials(code, client_id, client_secret, redirect_uri):
    # Exchange tokens from Google OAuth 2.0 endpoint.
    credentials = Credentials.from_client_info_and_code(
        client_info={"client_id": client_id, "client_secret": client_secret},
        code=code,
        redirect_uri=redirect_uri,
        request=Request(),
    )
    return credentials


class SocialUrlView(APIView):
    @swagger_auto_schema(
        tags=["social login"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        origin_url = request.build_absolute_uri()
        # user_agent= "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        # request.META['HTTP_USER_AGENT'] = user_agent
        client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        if "humascot.shop" in origin_url:
            redirect_uri = URI2
        elif "web4all.site" in origin_url:
            redirect_uri = URI3
        elif "web4all.store" in origin_url:
            redirect_uri = URI4
        else:
            redirect_uri = URI
        url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&disallow_webview=true&response_type=code&scope=email%20profile"
        return Response({"url": url}, status=200)


# Google Social Login
class GoogleLoginView(APIView):
    @swagger_auto_schema(
        tags=["social login"],
        request_body=PostUserSerializer,
        responses={200: "Success"},
    )
    def post(self, request):
        code = request.data.get("code")
        client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
        origin_url = request.build_absolute_uri()
        if "humascot.shop" in origin_url:
            redirect_uri = URI2
        elif "web4all.site" in origin_url:
            redirect_uri = URI3
        elif "web4all.store" in origin_url:
            redirect_uri = URI4
        else:
            redirect_uri = URI
        # user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        # request.META['HTTP_USER_AGENT'] = user_agent
        # Request an access token from Google API
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        id_token_str = token_json.get("id_token")  # string ID token
        # Get user information with access token
        try:
            idinfo = google_id_token.verify_oauth2_token(
                id_token_str, Request(), client_id
            )
            email = idinfo.get("email")
            profile_image = idinfo.get("picture")

        except ValueError as e:
            # Error handling
            pass

        email = idinfo.get("email")
        profile_image = idinfo.get("picture")

        try:
            # If the user already exists (if the user has registered)
            user = UserModel.objects.get(email=email)
            # Check if the account is cancelled.
            if user.is_active:

                store = StoreModel.objects.filter(seller=user).first()
                refresh = RefreshToken.for_user(user)
                refresh["email"] = user.email
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "user_id": user.id,
                        "user_name": user.nickname,
                        "is_first": False,  # Later changed to False
                        "store_id": store.id if store else False,
                        "origin_store_name": store.name if store else False,
                        "is_google": True,
                        "email": user.email if user.email else False,
                        "image": (
                            user.profile_image.url if user.profile_image else False
                        ),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "Users who have canceled their membership will not be able to log in!"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            random_nickname = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )  # Generate 6-digit random string

            # Proceed with membership registration if the user does not exist
            user = UserModel.objects.create_user(
                email=email, nickname=f"Google_{random_nickname}"
            )
            if profile_image:
                profile_image = download_image(profile_image)
                file_name = f"{random_nickname}.jpg"
                user.profile_image.save(file_name, profile_image)

            user.set_unusable_password()  # Create password
            user.save()

            store = StoreModel.objects.filter(seller=user).first()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "user_name": user.nickname,
                    "is_first": True,
                    "store_id": store.id if store else False,
                    "origin_store_name": store.name if store else False,
                    "is_google": True,
                    "email": user.email if user.email else False,
                    "image": user.profile_image.url if user.profile_image else False,
                },
                status=status.HTTP_200_OK,
            )


class SellerSignup(APIView):
    def get(self, request):
        return render(request, "user/google_seller.html")

    def post(self, request):
        with transaction.atomic():
            user_id = request.data.get("user_id")
            name = request.data.get("name")
            address = request.data.get("address")
            user = UserModel.objects.get(id=user_id)
            if not name or not address:
                return Response(
                    {"message": "Please enter all required information."},
                    status.HTTP_400_BAD_REQUEST,
                )
            if user.is_seller and not user.is_admin:
                return Response(
                    {"message": "You are already registered as a seller."},
                    status.HTTP_400_BAD_REQUEST,
                )

            serializer = SellerSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(seller_id=user_id)
                try:
                    user.is_seller = True
                    if not user.nickname:
                        user.nickname = name
                    user.save()
                except Exception as e:
                    return Response(
                        {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )

                return Response(
                    data={
                        "user_id": user.id,
                        "store_id": serializer.data.get("id"),
                        "user_name": user.nickname,
                        "origin_store_name": serializer.data.get("name"),
                        "email": user.email if user.email else False,
                        "image": (
                            user.profile_image.url if user.profile_image else False
                        ),
                    },
                    status=200,
                )
            return Response(
                {"message": "A problem has occurred."}, status.HTTP_400_BAD_REQUEST
            )


def download_image(url):
    response = requests.get(url)

    if response.status_code == 200:
        # Create a file in memory using ContentFile
        return ContentFile(response.content)
    else:
        return None


class CheckToken(APIView):

    def post(self, request):
        try:
            token = request.data.get("token")
            # token decode
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # Check expiration time
            expiration_time = decoded_token.get("exp")
            return Response({"result": "success"}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            # If the token has expired
            return Response({"result": "fail"}, status=status.HTTP_200_OK)
        except jwt.InvalidTokenError:
            # In case of invalid token
            return Response({"result": "fail"}, status=status.HTTP_200_OK)


def resize_image(image_data, output_size=(800, 600), quality=85):
    """
    Adjust the resolution of the image file and save it in JPEG format.
    :param image_data: Original image data (base64 encoded string).
    :param output_size: Size (width, height) of the image to be changed.
    :param quality: JPEG storage quality (1-100).
    :return: Changed image data (base64 encoded string).
    """
    try:
        # Convert image data to PIL image object
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # Change image size
        image = image.resize(output_size, Image.ANTIALIAS)

        # Save in JPEG format
        output_buffer = io.BytesIO()
        image.save(output_buffer, format="JPEG", quality=quality)
        output_data = base64.b64encode(output_buffer.getvalue()).decode()
        print(634)
        return output_data
    except Exception as e:
        print(e)
        return image_data


def my_page_render(request):
    return render(request, "user/my_page.html")


def find_password_render(request):
    return render(request, "user/find_pw.html")


def more_page_render(request):
    return render(request, "more.html")


def user_profile_render(request):
    return render(request, "user/profile.html")


def change_seller_render(request):
    return render(request, "user/change_seller.html")


def intro_render(request):
    return render(request, "intro.html")


def term_render(request):
    return render(request, "terms.html")


def policy_render(request):
    return render(request, "policy.html")


class UserListView(generics.ListAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Example: Require authentication


class UserDetailsView(generics.RetrieveAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Example: Require authentication
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
