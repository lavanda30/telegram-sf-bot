import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';
import TelegramBot from 'node-telegram-bot-api';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8080;

// Парсинг JSON для POST-запросов
app.use(express.json());

// Инициализация бота без polling — только через webhook
const bot = new TelegramBot(process.env.TG_TOKEN);
const BASE_URL = process.env.BASE_URL; // https://telegram-sf-bot.up.railway.app

// Устанавливаем webhook
bot.setWebHook(`${BASE_URL}/bot${process.env.TG_TOKEN}`);

// Функция для получения access_token по refresh_token
async function getAccessToken() {
  const response = await axios.post('https://login.salesforce.com/services/oauth2/token', null, {
    params: {
      grant_type: 'refresh_token',
      client_id: process.env.SF_CLIENT_ID,
      client_secret: process.env.SF_CLIENT_SECRET,
      refresh_token: process.env.SF_REFRESH_TOKEN
    }
  });
  return response.data.access_token;
}

// Эндпоинт для Telegram webhook
app.post(`/bot${process.env.TG_TOKEN}`, (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

// Обработчик команды /start
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, "Привет! Нажми /newcontact для создания Контакта.");
});

// Обработчик команды /newcontact
bot.onText(/\/newcontact/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, "Введите имя нового контакта:");

  bot.once('message', async (nameMsg) => {
    const name = nameMsg.text;

    bot.sendMessage(chatId, "Введите телефон нового контакта:");

    bot.once('message', async (phoneMsg) => {
      const phone = phoneMsg.text;

      try {
        const accessToken = await getAccessToken();

        const response = await axios.post(
          `${process.env.SF_INSTANCE_URL}/services/data/v57.0/sobjects/Contact__c/`,
          {
            Name: name,
            ClientName__c: phone
          },
          {
            headers: { Authorization: `Bearer ${accessToken}` }
          }
        );

        bot.sendMessage(chatId, `Контакт создан! Id: ${response.data.id}`);
      } catch (err) {
        console.error(err.response?.data || err.message);
        bot.sendMessage(chatId, `Ошибка при создании контакта: ${err.message}`);
      }
    });
  });
});

// Проверка сервера
app.get('/', (req, res) => {
  res.send('Telegram-SF bot is running.');
});

// Запуск сервера
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
