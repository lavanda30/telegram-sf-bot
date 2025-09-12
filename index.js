import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

const app = express();
app.use(express.json());

app.post('/telegram-webhook', async (req, res) => {
  const message = req.body.message;
  if (!message) return res.sendStatus(200);

  const chatId = message.chat.id;
  const text = message.text;

  if (text.startsWith('/newcontact')) {
    try {
      const accessToken = await axios.post(
        'https://login.salesforce.com/services/oauth2/token',
        null,
        {
          params: {
            grant_type: 'refresh_token',
            client_id: process.env.SF_CLIENT_ID,
            client_secret: process.env.SF_CLIENT_SECRET,
            refresh_token: process.env.SF_REFRESH_TOKEN
          }
        }
      ).then(r => r.data.access_token);

      await axios.post(
        `${process.env.SF_INSTANCE_URL}/services/data/v57.0/sobjects/Contact__c/`,
        { Name: "Имя от пользователя", ClientName__c: "Телефон" },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );

      await axios.post(`https://api.telegram.org/bot${process.env.TG_TOKEN}/sendMessage`, {
        chat_id: chatId,
        text: "Контакт создан!"
      });

    } catch (err) {
      console.error(err.response?.data || err.message);
      await axios.post(`https://api.telegram.org/bot${process.env.TG_TOKEN}/sendMessage`, {
        chat_id: chatId,
        text: "Ошибка при создании контакта"
      });
    }
  }

  res.sendStatus(200);
});

app.listen(process.env.PORT || 3000, () => console.log("Webhook сервер запущен"));
