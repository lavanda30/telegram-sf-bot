import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';
import TelegramBot from 'node-telegram-bot-api';

dotenv.config();

// Express-сервер для OAuth
const app = express();
const PORT = process.env.PORT || 3000;

// Telegram бот с polling
const bot = new TelegramBot(process.env.TG_TOKEN, { polling: true });
console.log('Бот запущен. Ждём сообщений...');

// Функция для получения нового access_token через refresh_token
async function getAccessToken() {
  try {
    const response = await axios.post('https://login.salesforce.com/services/oauth2/token', null, {
      params: {
        //console.log('!!!!!!!SF_CLIENT_ID!!!!!!! ', process.env.SF_CLIENT_ID);
        grant_type: 'refresh_token',
        client_id: process.env.SF_CLIENT_ID,
        client_secret: process.env.SF_CLIENT_SECRET,
        refresh_token: process.env.SF_REFRESH_TOKEN
      }
    });
    return response.data.access_token;
  } catch (err) {
    console.error('Ошибка при получении access_token:', err.response?.data || err.message);
    throw err;
  }
}

// Telegram команды
bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, "Привет! Нажми /newcontact для создания нового Contact__c.");
});

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
        console.error('Ошибка при создании Contact__c:', err.response?.data || err.message);
        bot.sendMessage(chatId, `Ошибка при создании контакта: ${err.message}`);
      }
    });
  });
});

// OAuth маршруты для Salesforce
app.get('/auth', (req, res) => {
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: process.env.SF_CLIENT_ID,
    redirect_uri: process.env.SF_REDIRECT_URI
  });
  res.redirect(`https://login.salesforce.com/services/oauth2/authorize?${params.toString()}`);
});

app.get('/oauth/callback', async (req, res) => {
  const { code } = req.query;
  if (!code) return res.status(400).send('No code provided');

  try {
    const response = await axios.post('https://login.salesforce.com/services/oauth2/token', null, {
      params: {
        grant_type: 'authorization_code',
        code,
        client_id: process.env.SF_CLIENT_ID,
        client_secret: process.env.SF_CLIENT_SECRET,
        redirect_uri: process.env.SF_REDIRECT_URI
      }
    });
    console.log('Salesforce tokens:', response.data);
    res.send('Login successful! Check logs for tokens.');
  } catch (err) {
    console.error(err.response?.data || err.message);
    res.status(500).send('Error exchanging code for token');
  }
});

// Запуск сервера
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
