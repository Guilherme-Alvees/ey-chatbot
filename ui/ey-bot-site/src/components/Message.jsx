import React from 'react';
import { Box, Typography, Avatar } from '@mui/material';

const Message = ({ text, isUser }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: isUser ? 'row-reverse' : 'row',
          alignItems: 'center',
          maxWidth: '70%',
        }}
      >
        <Avatar sx={{ bgcolor: isUser ? '#1976d2' : '#757575' }}>
          {isUser ? 'U' : 'B'}
        </Avatar>
        <Box
          sx={{
            ml: isUser ? 0 : 1,
            mr: isUser ? 1 : 0,
            p: 2,
            borderRadius: 2,
            bgcolor: isUser ? '#1976d2' : '#e0e0e0',
            color: isUser ? 'white' : 'black',
          }}
        >
          <Typography variant="body1">{text}</Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default Message;