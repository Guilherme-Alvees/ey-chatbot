import React, { useState } from 'react';
import { Box, TextField, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const InputArea = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', mt: 2 }}>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Send a message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        sx={{ flexGrow: 1 }}
      />
      <IconButton type="submit" color="primary" sx={{ ml: 1 }}>
        <SendIcon />
      </IconButton>
    </Box>
  );
};

export default InputArea;