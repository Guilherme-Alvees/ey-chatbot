import React from "react";
import { CssBaseline, Container } from "@mui/material";
import Chatbot from "./components/Chatbot";

function App() {
  return (
    <>
      <CssBaseline />
      <Container
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <Chatbot />
      </Container>
    </>
  );
}

export default App;
