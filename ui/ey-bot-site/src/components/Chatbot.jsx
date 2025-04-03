import React, { useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import Message from './Message';
import InputArea from './InputArea';
import axios from 'axios';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      text: 'Olá! Sou o chatbot de dados. Como posso ajudar?',
      isUser: false,
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message) => {
    // Adiciona mensagem do usuário
    setMessages((prev) => [...prev, { text: message, isUser: true }]);
    setIsLoading(true);

    try {
      // Chama a API
      const response = await axios.post(
        'https://chatbot-api-hs3febfij-guilhermealvees-projects.vercel.app/consulta',
        {
          pergunta: message,
        }
      );

      // Adiciona resposta do bot
      setMessages((prev) => [
        ...prev,
        { text: response.data.resposta, isUser: false },
      ]);
    } catch (error) {
      console.error('Erro ao chamar a API:', error);
      setMessages((prev) => [
        ...prev,
        {
          text: 'Desculpe, ocorreu um erro ao processar sua pergunta.',
          isUser: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        width: 350,
        height: 500,
        display: 'flex',
        flexDirection: 'column',
        p: 2,
      }}
    >
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
        EY Chatbot
      </Typography>
      <Box sx={{ flexGrow: 1, overflowY: 'auto', mb: 2 }}>
        {messages.map((msg, index) => (
          <Message key={index} text={msg.text} isUser={msg.isUser} />
        ))}
        {isLoading && (
          <Message text="Processando sua pergunta..." isUser={false} />
        )}
      </Box>
      <InputArea onSendMessage={handleSendMessage} />
    </Paper>
  );
};

export default Chatbot;