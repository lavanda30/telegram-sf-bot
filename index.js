import TelegramBot from 'node-telegram-bot-api';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const bot = new TelegramBot(process.env.TG_TOKEN, { polling: true });

// Функция для получения нового access_token через refresh_token
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

// Обработчик команды /start
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, "Привет, Анютка. Нажми /newcontact для создания Контакта.");
});

// Обработчик команды /newcontact
bot.onText(/\/newcontact/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, "Введите имя нового контакта:");
  
  bot.once('message', async (nameMsg) => {
    const name = nameMsg.text;

    bot.sendMessage(chatId, "Введите телефон нового контакта:");

    bot.once('message', async (lastMsg) => {
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

