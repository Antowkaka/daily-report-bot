from os import getenv

from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo.errors import ServerSelectionTimeoutError

from app.loggers import db_logger
from app.entities.user import UserEntity, GoalsType

load_dotenv()


class DatabaseService:
    _client: AsyncIOMotorClient
    _users_collection: AsyncIOMotorCollection
    _reports_collection: AsyncIOMotorCollection

    def __init__(self):
        client = AsyncIOMotorClient(
            getenv('MONGO_DB_HOST'),
            username=getenv('MONGO_DB_USERNAME'),
            password=getenv('MONGO_DB_PASSWORD'),
            authMechanism='SCRAM-SHA-1'
        )

        try:
            if client.is_primary:
                db = client['daily-report-bot']
                # defining main fields: collections and client
                self._client = client
                self._users_collection = db.users_collection
                self._reports_collection = db.reports_collection
                db_logger.info('Database successfully connected')
        except ServerSelectionTimeoutError:
            db_logger.error('Connection failed')

    async def create_user(self, user: UserEntity.model):
        await self._users_collection.insert_one(user)

    async def update_user_goals(self, tg_id: int, goals: GoalsType):
        await self._users_collection.update_one({'telegramID': tg_id}, {'$set': {'goals': goals}})

    async def delete_user(self, tg_id: int):
        await self._users_collection.delete_one({'telegramID': tg_id})

    async def get_user(self, tg_id: int):
        user = await self._users_collection.find_one({'telegramID': tg_id})

        return user
