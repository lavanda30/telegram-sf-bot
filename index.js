import express from 'express';
import bodyParser from 'body-parser';
import TelegramBot from 'node-telegram-bot-api';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

// Простой корневой маршрут
app.get('/', (req, res) => res.send('Server is running'));

// === Salesforce OAuth ===
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
    res.send('Успешный логин! Посмотри refresh_token в логах Railway.');
  } catch (err) {
    console.error(err.response?.data || err.message);
    res.status(500).send('Ошибка при обмене кода на токен');
  }
});

// === Telegram Bot ===
const bot = new TelegramBot(process.env.TG_TOKEN);
const webhookUrl = `${process.env.BASE_URL}/bot${process.env.TG_TOKEN}`;

// Установка webhook
bot.setWebHook(webhookUrl);

// Обработка входящих сообщений через webhook
app.post(`/bot${process.env.TG_TOKEN}`, async (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

// Команды Telegram
bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, "Привет! Нажми /newcontact для создания нового Contact__c.");
});

bot.onText(/\/newcontact/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, "Введите имя нового контакта:");

  bot.once('message', async (nameMsg) => {
    const name = nameMsg.text;

    bot.sendMessage(chatId, "Введите телефон контакта:");

    bot.once('message', async (phoneMsg) => {
      const phone = phoneMsg.text;

      try {
        // Получение access_token
        const tokenRes = await axios.post('https://login.salesforce.com/services/oauth2/token', null, {
          params: {
            grant_type: 'refresh_token',
            client_id: process.env.SF_CLIENT_ID,
            client_secret: process.env.SF_CLIENT_SECRET,
            refresh_token: process.env.SF_REFRESH_TOKEN
          }
        });

        const accessToken = tokenRes.data.access_token;

        // Создание Contact__c
        const sfRes = await axios.post(
          `${process.env.SF_INSTANCE_URL}/services/data/v57.0/sobjects/Contact__c/`,
          { Name: name, Phone__c: phone },
          { headers: { Authorization: `Bearer ${accessToken}` } }
        );

        bot.sendMessage(chatId, `Контакт создан! Id: ${sfRes.data.id}`);
      } catch (err) {
        console.error(err.response?.data || err.message);
        bot.sendMessage(chatId, `Ошибка при создании контакта: ${err.message}`);
      }
    });
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Webhook URL: ${webhookUrl}`);
});
