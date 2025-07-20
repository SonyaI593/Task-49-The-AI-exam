import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from typing import Dict, List

def parse_program(url: str) -> Dict:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        program_data = {
            'title': soup.find('h1', class_='Information_information__header__fab3I').text.strip() 
                     if soup.find('h1', class_='Information_information__header__fab3I') 
                     else "Название не найдено",
            'description': "",
            'courses': []
        }
        
        return program_data
    
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")
        return {
            'title': "Ошибка загрузки",
            'description': "",
            'courses': []
        }
    
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")
        return {
            'title': "Ошибка загрузки",
            'description': "",
            'courses': []
        }

# Загрузка данных программ
programs = {
    'ai': parse_program('https://abit.itmo.ru/program/master/ai'),
    'ai_product': parse_program('https://abit.itmo.ru/program/master/ai_product')
}

# Логика рекомендаций
def recommend_courses(program: str, background: str) -> List[str]:
    ai_keywords = ['машинное обучение', 'нейросети', 'алгоритмы']
    product_keywords = ['управление', 'продукт', 'бизнес']
    
    recommendations = []
    for course in programs[program]['courses']:
        if course['type'] == 'Выборный':
            if program == 'Искусственный интеллект' and any(kw in course['name'].lower() for kw in ai_keywords):
                recommendations.append(course['name'])
            elif program == 'Управление ИИ-продуктами' and any(kw in course['name'].lower() for kw in product_keywords):
                recommendations.append(course['name'])
    
    return recommendations[:3]  # Топ-3 рекомендации

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Искусственный интеллект", callback_data='ai')],
        [InlineKeyboardButton("Управление ИИ-продуктами", callback_data='ai_product')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Я помогу выбрать магистерскую программу в ИТМО.\n"
        "Сначала выбери программу для сравнения:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    context.user_data['program'] = query.data
    await query.edit_message_text(
        f"Выбрана программа: {programs[query.data]['title']}\n"
        "Расскажи кратко о своем бэкграунде (например: 'У меня бакалавриат по CS, интересуюсь ML')"
    )

async def handle_message(update: Update, context: CallbackContext):
    if 'program' not in context.user_data:
        await update.message.reply_text("Пожалуйста, сначала выбери программу через /start")
        return
    
    background = update.message.text
    context.user_data['background'] = background
    
    program = context.user_data['program']
    recommendations = recommend_courses(program, background)
    
    response = (
        f"На основе твоего бэкграунда ('{background}') "
        f"для программы {programs[program]['title']} рекомендую:\n\n" +
        "\n".join(f"• {course}" for course in recommendations) +
        "\n\nМожешь задать вопросы про конкретные курсы или выбрать другую программу через /start"
    )
    
    await update.message.reply_text(response)

def main():
    application = Application.builder().token("TOKEN").build()  #замена реального токена для сохранения конфидициальности
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()