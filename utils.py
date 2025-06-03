from aiogram import types
import config

def get_item_by_index(d, index, only_value=True):
    """
    Отримує ключ та значення з словника за індексом, зручно для роботи з config.menu
    коли ми передаємо не назву ключа в JSON, а індекс.
    """
    key = list(d.keys())[index]
    return d[key] if only_value else (key, d[key])

def get_data_by_index(index, include_name_path=False):
    """
    Опрацьовуємо всі індеки по порядку, та отримаємо те data, яке нам потрібно
    Іншими словами, проганяємо всі минулі вибори, та отримуємо data кожного, щоб отримати необхідне поточне значення data.
    """
    data = config.menu
    if include_name_path:
        name_path = ""

    for i in index:
        name, data = get_item_by_index(data, int(i), only_value=False)

        if include_name_path:
            name_path += f"{name} ➔ "

    return (name_path, data) if include_name_path else data

async def check_username(message: types.Message | types.CallbackQuery):
    """
    Перевіряє, чи користувач має встановлений username в профілі.
    Якщо ні, то просить його встановити та надіслати команду /start.
    """
    if not message.from_user.username:
        await message.answer(
            "⚠️Ви не вказали username в налаштуваннях профілю, будь ласка, вкажіть його, після чого надішліть команду /start щоб продовжити роботу з ботом.\n\n"
            '<a href="https://telegra.ph/Pokrokova-%D1%96nstrukc%D1%96ya-yak-vstanoviti-abo-zm%D1%96niti-username-%D1%96mya-koristuvacha-u-Telegram-06-02">📔Покрокова інструкція з встановлення username</a>',
            disable_web_page_preview=True
        )
        return False
    return True
