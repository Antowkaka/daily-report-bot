import logging
from os import getenv

from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure

from app.loggers import db_logger

load_dotenv()


class DatabaseService:
    _client: AsyncIOMotorClient
    _users_collection: AsyncIOMotorCollection
    _reports_collection: AsyncIOMotorCollection

    def __init__(self):
        try:
            client = AsyncIOMotorClient(
                getenv('MONGO_DB_HOST'),
                username=getenv('MONGO_DB_USERNAME'),
                password=getenv('MONGO_DB_PASSWORD'),
                authMechanism='SCRAM-SHA-1'
            )
            db = client['daily-report-bot']

            # defining main fields: collections and client
            self._client = client
            self._users_collection = db.users_collection
            self._reports_collection = db.reports_collection
            db_logger.info('Database successfully connected')
        except ConnectionFailure:
            db_logger.info('Connection failed')

    async def create_user(self, username: str, full_name: str, tg_id: int):
        user = {
            'username': username,
            'fullName': full_name,
            'telegramID': tg_id
        }

        await self._users_collection.insert_one(user)

    async def delete_user(self, tg_id: int):
        await self._users_collection.delete_one({'telegramID': tg_id})
