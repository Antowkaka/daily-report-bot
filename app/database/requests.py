from .models.user_model import User


def create_user(username: str, full_name: str, tg_id: int):
    user = User(username=username, full_name=full_name, tg_id=tg_id)
    user.save()
