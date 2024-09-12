import json

from app.loggers import error_logger

with open("text_data.json", mode="r", encoding="utf-8") as read_file:
    text_data = json.load(read_file)


def get_text(key: str) -> str:
    try:
        text = text_data[key]

        return text
    except KeyError:
        error_logger.error(f'get_text error for key {key}')
