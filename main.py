from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import config
import asyncio
import logging
import handlers

# Логування
logging.basicConfig(level=logging.DEBUG)

# Об'єкт бота
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

# Диспетчер
dp = Dispatcher()
dp.include_router(handlers.router)

# Запуск процесу полінгу нових оновлень
async def main():
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())