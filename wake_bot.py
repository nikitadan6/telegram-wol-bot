import os
import socket
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
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

    def start(self, update, context):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            update.message.reply_text("Access denied")
            return
        update.message.reply_text("Bot is ready. Commands: /wake /status /help")

    def wake(self, update, context):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            update.message.reply_text("Access denied")
            return
        update.message.reply_text("Sending WoL packet...")
        if self.wake_pc():
            update.message.reply_text("WoL packet sent! Computer should start in 1-2 minutes.")
        else:
            update.message.reply_text("Error sending WoL")

    def status(self, update, context):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            update.message.reply_text("Access denied")
            return
        update.message.reply_text(f"Bot status: Active\nMAC: {self.mac}")

    def help(self, update, context):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            update.message.reply_text("Access denied")
            return
        update.message.reply_text("Commands: /wake - wake PC, /status - bot status, /help - help")

    def run(self):
        updater = Updater(self.token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("wake", self.wake))
        dispatcher.add_handler(CommandHandler("status", self.status))
        dispatcher.add_handler(CommandHandler("help", self.help))
        updater.start_polling()
        updater.idle()

if __name__ == "__main__":
    bot = WakeBot()
    bot.run()