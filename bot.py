import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from config import BOT_TOKEN, ADMIN_IDS, WEBAPP_URL
from database import db
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌿 Открыть магазин", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📋 Каталог", callback_data='catalog')],
        [InlineKeyboardButton("ℹ️ О нас", callback_data='about')]
    ]
    
    if update.effective_user.id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Админ-панель", callback_data='admin')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌿 Добро пожаловать в магазин травяных растений!\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

# Каталог товаров
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    categories = db.get_categories()
    keyboard = [[InlineKeyboardButton(cat, callback_data=f'cat_{cat}')] 
                for cat in categories]
    keyboard.append([InlineKeyboardButton("« Назад", callback_data='back')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📋 Выберите категорию:", reply_markup=reply_markup)

# Показать товары категории
async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace('cat_', '')
    products = db.get_products_by_category(category)
    
    if not products:
        await query.edit_message_text(
            f"В категории '{category}' пока нет товаров.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад", callback_data='catalog')
            ]])
        )
        return
    
    text = f"🌿 *{category}*\n\n"
    keyboard = []
    
    for product in products:
        status = "✅" if product['in_stock'] else "❌"
        text += f"{status} *{product['name']}* - {product['price']} ₽\n"
        text += f"_{product['description']}_\n\n"
        keyboard.append([InlineKeyboardButton(
            f"{'🛒' if product['in_stock'] else '❌'} {product['name']}", 
            callback_data=f"product_{product['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("« Назад", callback_data='catalog')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# Админ-панель
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if update.effective_user.id not in ADMIN_IDS:
        await query.answer("У вас нет доступа к админ-панели!", show_alert=True)
        return
    
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить товар", callback_data='admin_add')],
        [InlineKeyboardButton("✏️ Редактировать товар", callback_data='admin_edit')],
        [InlineKeyboardButton("🗑 Удалить товар", callback_data='admin_delete')],
        [InlineKeyboardButton("📦 Заказы", callback_data='admin_orders')],
        [InlineKeyboardButton("« Назад", callback_data='back')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "⚙️ *Админ-панель*\n\nВыберите действие:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Список товаров для редактирования
async def admin_edit_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    products = db.get_all_products()
    
    if not products:
        await query.edit_message_text(
            "Товаров пока нет.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад", callback_data='admin')
            ]])
        )
        return
    
    keyboard = [[InlineKeyboardButton(
        f"{p['name']} ({p['price']} ₽)", 
        callback_data=f"edit_{p['id']}"
    )] for p in products]
    keyboard.append([InlineKeyboardButton("« Назад", callback_data='admin')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "✏️ Выберите товар для редактирования:",
        reply_markup=reply_markup
    )

# Удаление товара
async def admin_delete_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    products = db.get_all_products()
    
    if not products:
        await query.edit_message_text(
            "Товаров нет.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад", callback_data='admin')
            ]])
        )
        return
    
    keyboard = [[InlineKeyboardButton(
        f"🗑 {p['name']}", 
        callback_data=f"del_{p['id']}"
    )] for p in products]
    keyboard.append([InlineKeyboardButton("« Назад", callback_data='admin')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🗑 Выберите товар для удаления:",
        reply_markup=reply_markup
    )

# Подтверждение удаления
async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = int(query.data.replace('del_', ''))
    
    product = db.get_product(product_id)
    if product:
        db.remove_product(product_id)
        await query.answer(f"✅ Товар '{product['name']}' удален!", show_alert=True)
        await admin_delete_list(update, context)
    else:
        await query.answer("Товар не найден!", show_alert=True)

# Обработка данных из WebApp
async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    
    if data.get('type') == 'order':
        order_id = db.add_order(
            user_id=update.effective_user.id,
            username=update.effective_user.username or "Без имени",
            products=data['products'],
            total=data['total'],
            contact=data['contact']
        )
        
        # Уведомление администраторам
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🔔 *Новый заказ #{order_id}*\n\n"
                    f"От: @{update.effective_user.username}\n"
                    f"Сумма: {data['total']} ₽\n"
                    f"Контакт: {data['contact']}",
                    parse_mode='Markdown'
                )
            except:
                pass
        
        await update.message.reply_text(
            f"✅ Заказ #{order_id} принят!\n\n"
            f"Сумма: {data['total']} ₽\n"
            f"Скоро с вами свяжется менеджер."
        )

# Обработчик callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'catalog':
        await show_catalog(update, context)
    elif data.startswith('cat_'):
        await show_category_products(update, context)
    elif data == 'admin':
        await admin_panel(update, context)
    elif data == 'admin_edit':
        await admin_edit_list(update, context)
    elif data == 'admin_delete':
        await admin_delete_list(update, context)
    elif data.startswith('del_'):
        await confirm_delete(update, context)
    elif data == 'back':
        await start(update, context)
    elif data == 'about':
        await query.answer()
        await query.edit_message_text(
            "🌿 *О нас*\n\n"
            "Магазин качественных травяных растений.\n"
            "Все товары натуральные и сертифицированные.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад", callback_data='back')
            ]]),
            parse_mode='Markdown'
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
