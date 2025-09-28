import os
import socket
import logging
import subprocess
import platform
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class WakeBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN', '8313500508:AAG0SFdohCyrtWTvacjPZqECVZH1bbd4a5g')
        self.allowed_users = [int(x) for x in os.getenv('ALLOWED_USERS', '702965644').split(',')]
        self.mac = os.getenv('MAC_ADDRESS', '74-56-3C-AA-E7-9B')

    def wake_pc(self):
        try:
            mac_clean = self.mac.replace('-', '').replace(':', '')
            mac_bytes = bytes.fromhex(mac_clean)
            magic_packet = b'\xff' * 6 + mac_bytes * 16
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, ('255.255.255.255', 9))
            sock.close()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def check_pc_status(self):
        """Проверка статуса компьютера через ping"""
        try:
            target_ip = "192.168.31.195"
            
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "1", target_ip]
            
            result = subprocess.run(command, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Status check error: {e}")
            return False

    def shutdown_pc(self):
        """Выключение компьютера"""
        try:
            if platform.system().lower() == "windows":
                subprocess.run(["shutdown", "/s", "/t", "60"])
                return True, "Computer will shutdown in 60 seconds"
            else:
                subprocess.run(["shutdown", "-h", "+1"])
                return True, "Computer will shutdown in 1 minute"
        except Exception as e:
            return False, f"Error: {e}"

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text("Access denied")
            return
        await update.message.reply_text(
            "Bot is ready. Commands:\n"
            "/wake - Wake up PC\n"
            "/status - Check PC status\n" 
            "/shutdown - Shutdown PC\n"
            "/help - Help"
        )

    async def wake(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text("Access denied")
            return
        await update.message.reply_text("Sending WoL packet...")
        if self.wake_pc():
            await update.message.reply_text("WoL packet sent! Computer should start in 1-2 minutes.")
        else:
            await update.message.reply_text("Error sending WoL")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text("Access denied")
            return
        
        await update.message.reply_text("Checking PC status...")
        
        if self.check_pc_status():
            await update.message.reply_text("🟢 PC is ONLINE")
        else:
            await update.message.reply_text("🔴 PC is OFFLINE")

    async def shutdown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text("Access denied")
            return
        
        await update.message.reply_text("Initiating shutdown...")
        success, message = self.shutdown_pc()
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text("Access denied")
            return
        await update.message.reply_text(
            "Commands:\n"
            "/wake - Wake up PC using Wake-on-LAN\n"
            "/status - Check if PC is online\n"
            "/shutdown - Shutdown PC\n" 
            "/help - Show this help"
        )

    def run(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("wake", self.wake))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(CommandHandler("shutdown", self.shutdown))
        application.add_handler(CommandHandler("help", self.help))
        application.run_polling()

if __name__ == "__main__":
    bot = WakeBot()
    bot.run()