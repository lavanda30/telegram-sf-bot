import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Функция для получения access_token через refresh_token
async function getAccessToken() {
  try {
    const response = await axios.post('https://login.salesforce.com/services/oauth2/token', null, {
      params: {
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

// Endpoint для Telegram вебхука
app.post(`/telegram-webhook`, async (req, res) => {
  const message = req.body.message;

  if (!message || !message.text) {
    return res.sendStatus(200);
  }

  const chatId = message.chat.id;
  const text = message.text.trim();

  if (text === '/start') {
    await sendTelegramMessage(chatId, "Привет! Нажми /newcontact для создания нового контакта.");
  } else if (text === '/newcontact') {
    await sendTelegramMessage(chatId, "Введите имя нового контакта:");

    // Запоминаем состояние пользователя (в простом виде для примера)
    userState[chatId] = { step: 'awaiting_name' };
  } else if (userState[chatId]) {
    const state = userState[chatId];

    if (state.step === 'awaiting_name') {
      state.name = text;
      state.step = 'awaiting_phone';
      await sendTelegramMessage(chatId, "Введите телефон нового контакта:");
    } else if (state.step === 'awaiting_phone') {
      state.phone = text;

      try {
        const accessToken = await getAccessToken();

        const response = await axios.post(
          `${process.env.SF_INSTANCE_URL}/services/data/v57.0/sobjects/Contact__c/`,
          {
            Name: state.name,
            ClientName__c: state.phone
          },
          {
            headers: { Authorization: `Bearer ${accessToken}` }
          }
        );

        await sendTelegramMessage(chatId, `Контакт создан! Id: ${response.data.id}`);
      } catch (err) {
        console.error('Ошибка при создании Contact__c:', err.response?.data || err.message);
        await sendTelegramMessage(chatId, `Ошибка при создании контакта: ${err.message}`);
      }

      // Очищаем состояние пользователя
      delete userState[chatId];
    }
  }

  res.sendStatus(200);
});

// Простая память для состояний пользователей
const userState = {};

// Функция для отправки сообщений через Telegram API
async function sendTelegramMessage(chatId, text) {
  try {
    await axios.post(`https://api.telegram.org/bot${process.env.TG_TOKEN}/sendMessage`, {
      chat_id: chatId,
      text
    });
  } catch (err) {
    console.error('Ошибка при отправке сообщения в Telegram:', err.response?.data || err.message);
  }
}

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Webhook URL: ${process.env.BASE_URL}/telegram-webhook`);
});
