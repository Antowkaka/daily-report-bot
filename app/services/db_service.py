from os import getenv
from datetime import datetime, timedelta
import pytz

from dotenv import load_dotenv

from bson.codec_options import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo.errors import ServerSelectionTimeoutError

from app.loggers import db_logger
from app.entities.user import UserEntity, GoalsType
from app.entities.goal import GoalEntity
from app.entities.report import ReportEntity
from app.utils import validate_last_week_dates

load_dotenv()

kyiv_tz = pytz.timezone('Europe/Kyiv')


class DatabaseService:
    _client: AsyncIOMotorClient
    _users_collection: AsyncIOMotorCollection
    _reports_collection: AsyncIOMotorCollection

    def __init__(self):
        client = AsyncIOMotorClient(
            getenv('MONGO_DB_HOST'),
            username=getenv('MONGO_DB_USERNAME'),
            password=getenv('MONGO_DB_PASSWORD'),
            authMechanism='SCRAM-SHA-1',
        )

        try:
            if client.is_primary:
                db = client['daily-report-bot']
                # define timezone
                options = CodecOptions(tz_aware=True, tzinfo=kyiv_tz)

                # defining main fields: collections and client
                self._client = client
                self._users_collection = db.users_collection
                self._reports_collection = db.reports_collection.with_options(codec_options=options)
                db_logger.info('Database successfully connected')
        except ServerSelectionTimeoutError:
            db_logger.error('Connection failed')

    @property
    def client(self):
        return self._client

    async def create_user(self, user: UserEntity.model):
        await self._users_collection.insert_one(user)

    async def set_user_goals(self, tg_id: int, goals: GoalsType):
        await self._users_collection.update_one({'telegramID': tg_id}, {'$set': {'goals': goals}})

    async def add_new_user_goal(self, tg_id: int, goal_field: str, goal: GoalEntity.model):
        updated_user = await self._users_collection.find_one_and_update({
            'telegramID': tg_id},
            {'$set': {f'goals.{goal_field}': goal}},
            return_document=True
        )

        return updated_user

    async def update_user_goal(self, tg_id: int, goal_field: str, new_value: int):
        updated_user = await self._users_collection.find_one_and_update({
            'telegramID': tg_id},
            {'$set': {f'goals.{goal_field}.goalValue': new_value}},
            return_document=True
        )

        return updated_user

    async def update_user_training_type_goal(self, tg_id: int, new_type: str):
        await self._users_collection.update_one({
            'telegramID': tg_id},
            {'$set': {f'goals.trainingGoalType.goalValue': new_type}},
        )

    async def delete_user_goal(self, tg_id: int, goal_field: str):
        updated_user = await self._users_collection.find_one_and_update({
            'telegramID': tg_id},
            {'$unset': {f'goals.{goal_field}': ''}},
            return_document=True
        )

        return updated_user

    async def delete_user(self, tg_id: int):
        await self._users_collection.delete_one({'telegramID': tg_id})

    async def get_user(self, tg_id: int):
        user = await self._users_collection.find_one({'telegramID': tg_id})

        return user

    async def create_report(self, report: ReportEntity):
        report.set_created_at(datetime.now(pytz.timezone('Europe/Kyiv')))

        await self._reports_collection.insert_one(report.model)

    async def delete_all_reports(self, user_tg_id: int):
        await self._reports_collection.delete_many({'userTelegramID': user_tg_id})

    async def get_last_report(self):
        return await self._reports_collection.find_one(sort=[('_id', -1)])

    async def get_last_week_reports(self):
        now = datetime.now(kyiv_tz)
        last_week = now - timedelta(days=7)

        # Query to find documents where 'createdAt' is within the last 7 days
        reports_cursor = self._reports_collection.find({
            'createdAt': {
                '$gte': last_week,
                '$lt': now
            }
        })

        last_week_reports = await reports_cursor.to_list(7)
        remaining_days = validate_last_week_dates(last_week_reports)

        return last_week_reports, remaining_days
