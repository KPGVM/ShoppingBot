from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram import Router
from utils import *


router = Router()

@router.message(Command("start"))
@router.callback_query(F.data == "start")
async def start_command(message: types.Message | types.CallbackQuery):
    if isinstance(message, types.CallbackQuery):
        type_message = "callback_query"
    else:
        type_message = "message"

    if not await check_username(message):
        return

    # Перебираємо всі кореневі кнопки з config.menu та додаємо їх в клавіатуру
    builder = InlineKeyboardBuilder()
    for number_button, name_button in enumerate(config.menu):
        builder.add(types.InlineKeyboardButton(text=name_button, callback_data=f"menu|{number_button}"))

    builder.add(types.InlineKeyboardButton(text="🧑‍💻Розробник боту ", callback_data="developer"))
    builder.max_width = 2
    builder.adjust()


    if type_message == "callback_query":
        await message.message.edit_text(
            f"Привіт! Я бот-менеджер магазину <b>{config.name_store}</b>, виберіть з меню нижче, що ви хочете зробити.",
            reply_markup=builder.as_markup(),
        )
    else:
        await message.answer(
            f"Привіт! Я бот-менеджер магазину <b>{config.name_store}</b>, виберіть з меню нижче, що ви хочете зробити.",
            reply_markup=builder.as_markup(),
        )

@router.callback_query(F.data.startswith("menu|"))
async def menu_callback(callback: types.CallbackQuery):
    if not await check_username(callback):
        return

    # Трошки темінології:
    #   index - це list з індексами, за якими ми переходили по меню
    #   по їх можна отримати минулий шлях, поточну data, можна сказати що це посилання як в інтернеті
    #   
    #   data - це те, що ми отримуємо з config.menu, та що ми будемо віддавати в кнопки
    #   спочатку ми отримуємо значення data через індекси, через "прогон" по всім його значенням
    #   а потім в залежності від того, чи це dict чи list, ми формуємо кнопки
    #   та якщо це список, то це будуть фінальні кнопки



    # Спочатку отримуємо індекс-(и) з callback.data та отримуємо в змінну data те, що нам
    # потім потрібно опрацювати та додати в кнопки.
    index = callback.data.split("|")
    index.pop(0)  # Видаляємо перший елемент, який є "menu"

    current_path = callback.data  # Шлях до поточного меню
    current_index_list = "|".join(index)  # Збираємо індекс для поточного меню
    previous_path = "menu|" + "|".join(index[:-1])  # Збираємо шлях до минулого меню

    if len(index) == 1:
        index = int(index[0])
        data = get_item_by_index(config.menu, index)
        button_back = types.InlineKeyboardButton(text="🔙Назад", callback_data="start")
    else:
        data = get_data_by_index(index)

        button_back = types.InlineKeyboardButton(text="🔙Назад", callback_data=previous_path)


    
    match data:
        # Якщо data - це dict, то це означає, що ми маємо далі дати не фінальні вибори
        case dict():
            builder = InlineKeyboardBuilder()

            for number_button, name_button in enumerate(data):
                builder.add(types.InlineKeyboardButton(text=name_button, callback_data=f"{current_path}|{number_button}"))
        
        # Якщо data - це list, то це означає, що ми маємо дати фінальні вибори
        case list():
            builder = InlineKeyboardBuilder()

            for i in range(len(data)):
                builder.add(types.InlineKeyboardButton(text=data[i], callback_data=f"final_choose|{current_index_list}|{i}"))

    builder.add(button_back)
    builder.max_width = 1
    builder.adjust()


    await callback.message.edit_text(
        text="⛓️Оберіть опцію:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("final_choose|"))
async def final_choose_callback(callback: types.CallbackQuery):
    index = callback.data.split("|")
    index.pop(0)  # Видаляємо перший елемент, який є "final_choose"

    current_index_list = "|".join(index)  # Збираємо індекс для поточного меню
    previous_path = "menu|" + "|".join(index[:-1])  # Збираємо шлях до минулого меню
    final_index = int(index[-1]) # Отримуємо фінальний індекс, який ми вибрали

    # Видаляємо останній елемент з index, оскільки це фінальний вибір, і ми його отримаємо
    # з data передостаннього індексу, який є list[str]
    index.pop()


    # Змінна для того, щоб потім виводити сюди всі назви виборів, які ми зробили
    path_text = ""

    # Отримуємо дані за індексами, які ми отримали з callback.data
    path_text, data = get_data_by_index(index, include_name_path=True)

    # Додаємо за допомогою фінального значення data, яке є list[str] назву останнього вибору
    final_choose_text = data[final_index]
    path_text += final_choose_text

    callback_data_confirm = "confirm_order" + "|" + current_index_list

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✅Підтвердити замовлення", callback_data=callback_data_confirm))
    builder.add(types.InlineKeyboardButton(text="🔙Назад", callback_data=previous_path))
    builder.max_width = 2
    builder.adjust()

    await callback.message.edit_text(
        text="<b>✅Підтвердіть свій вибір</b>\n" \
        f"🎛Ваш вибір: <code>{path_text}</code>\n\n" \
        "📬Після підтвердження ваш вибір надішлеться адміністрації",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("confirm_order|"))
async def confirm_order_callback(callback: types.CallbackQuery):
    index = callback.data.split("|")
    index.pop(0)  # Видаляємо перший елемент, який є "confirm_order"
    final_index = int(index[-1])  # Отримуємо фінальний індекс, який ми вибрали

    index.pop()  # Видаляємо останній елемент, який є фінальним вибором
    path_text, data = get_data_by_index(index, include_name_path=True)

    path_text += data[final_index]  # Додаємо фінальний вибір до тексту


    # Формуємо текст повідомлення, яке буде надіслано адміністратору
    message_text = f"<b>✅Нове замовлення від користувача {callback.from_user.full_name} (@{callback.from_user.username})</b>\n\n" \
                   f"🎛Вибір: <code>{path_text}</code>\n" \
                   f"📬ID користувача: <code>{callback.from_user.id}</code>"

    await callback.bot.send_message(chat_id=config.ID_CHAT_ORDERS, text=message_text)



    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔙Назад до меню", callback_data="start"))
    builder.adjust()


    await callback.message.edit_text(
        text="✅Ваше замовлення надіслано адміністрації!",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "developer")
async def developer_callback(query: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔙Назад", callback_data="start"))
    
    await query.message.edit_text(
        text="Розробник боту:\n" \
              "🔗Посилання на GitHub: https://github.com/KPGVM\n" \
              "📱Telegram для зв'язку: @ana_earabiun (<b>Я НЕ ПРОДАВЕЦЬ, ЛИЦЕ РОЗРОБНИК</b>)\n\n" \
              "Буду не проти, якщо ви замовите у мене розробку бота в Telegram😇",
        reply_markup=builder.as_markup(),
        disable_web_page_preview=True
    )
