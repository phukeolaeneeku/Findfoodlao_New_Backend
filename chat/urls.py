from django.urls import path

from . import views
from .views import RoomView, ChatListView

urlpatterns = [
    # For page render
    path("", views.chat_list_render, name="index"),
    path("room/<int:store_id>", views.chatroom_render, name="room"),
    # For communication
    path("list", ChatListView.as_view(), name="ChatListView"),
    path("list/<int:goods_id>", ChatListView.as_view(), name="ChatListView"),
    path("room-connect/<str:store_id>", RoomView.as_view(), name="room"),
    # path("<str:store_id>/<str:user_id>/", RoomView.as_view(), name="room"),
]
