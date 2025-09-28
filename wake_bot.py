import os
import socket
import logging
from dotenv import load_dotenv

print("🤖 Запуск бота в облаке Render...")

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

class WakeBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN', '8313500508:AAG0SFdohCyrtWTvacjPZqECVZH1bbd4a5g')
        self.allowed_users = [int(x) for x in os.getenv('ALLOWED_USERS', '702965644').split(',')]
        self.mac = os.getenv('MAC_ADDRESS', '74-56-3C-AA-E7-9B')
        print("✅ Бот инициализирован в облаке")

    def wake_pc(self):
        try:
            print(f"📡 Отправка WoL пакета на MAC: {self.mac}")
            mac_clean = self.mac.replace('-', '').replace(':', '')
            mac_bytes = bytes.fromhex(mac_clean)
            
            magic_packet = b'\xff' * 6 + mac_bytes * 16
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, ('255.255.255.255', 9))
            sock.close()
            
            print("✅ WoL пакет отправлен из облака")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки WoL: {e}")
            return False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        print(f"👤 Команда /start от пользователя {user_id}")
        
        if user_id not in self.allowed_users:
            await update.message.reply_text("❌ Доступ запрещен")
            return
            
        await update.message.reply_text(
            "🤖 Бот управления компьютером\n\n"
            "Команды:\n"
            "/wake - Включить компьютер через WoL\n"
            "/status - Проверить статус бота\n"
            "/help - Помощь"
        )

    async def wake(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        print(f"👤 Команда /wake от пользователя {user_id}")
        
        if user_id not in self.allowed_users:
            await update.message.reply_text("❌ Доступ запрещен")
            return
            
        await update.message.reply_text("🖥️ Отправляю команду Wake-on-LAN...")
        
        if self.wake_pc():
            await update.message.reply_text("✅ Команда WoL отправлена! Компьютер должен включиться через 1-2 минуты.")
        else:
            await update.message.reply_text("❌ Ошибка отправки команды WoL")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text("❌ Доступ запрещен")
            return
            
        await update.message.reply_text(
            f"🤖 Статус бота:\n"
            f"✅ Активен\n"
            f"👤 Пользователи: {len(self.allowed_users)}\n"
            f"📡 MAC: {self.mac}"
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text("❌ Доступ запрещен")
            return
            
        await update.message.reply_text(
            "📖 Помощь:\n\n"
            "/wake - Включить компьютер\n"
            "/status - Статус бота\n"
            "/help - Справка"
        )

    def run(self):
        try:
            print("🔄 Создание приложения...")
            application = Application.builder().token(self.token).build()
            
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("wake", self.wake))
            application.add_handler(CommandHandler("status", self.status))
            application.add_handler(CommandHandler("help", self.help))
            
            print("✅ Бот запущен и ожидает сообщений...")
            
            application.run_polling()
            
        except Exception as e:
            print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    bot = WakeBot()
    bot.run()