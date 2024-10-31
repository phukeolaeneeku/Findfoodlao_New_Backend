from django.db import models
from users.models import UserModel
from store.models import StoreModel


class RoomModel(models.Model):
    class Meta:
        db_table = "room"
        verbose_name_plural = "1. Chat room list"

    store = models.ForeignKey(
        StoreModel, on_delete=models.CASCADE, verbose_name="store", null=True, blank=True
    )
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, verbose_name="user", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class MessageModel(models.Model):
    class Meta:
        verbose_name_plural = "2. Message details"

    # category = (("seller", "seller"), ("user", "user"))
    room = models.ForeignKey(RoomModel, on_delete=models.CASCADE, verbose_name="chat room")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    caller = models.CharField(max_length=100, verbose_name="Caller")  # 1=Shop, 2=User

    def __str__(self):
        return str(self.room.id)

    def last_30_messages(self, room_id):
        return MessageModel.objects.filter(room_id=room_id).order_by('created_at')[:30]
