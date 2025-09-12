import express from 'express';
import TelegramBot from 'node-telegram-bot-api';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(express.json());

const bot = new TelegramBot(process.env.TG_TOKEN);
const BASE_URL = process.env.BASE_URL; // твой URL Railway
const PORT = process.env.PORT || 3000;

// Устанавливаем webhook
bot.setWebHook(`${BASE_URL}/bot${process.env.TG_TOKEN}`);

// Telegram будет присылать апдейты сюда
app.post(`/bot${process.env.TG_TOKEN}`, (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

// Пример команды
bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, 'Привет! Бот работает через webhook!');
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
