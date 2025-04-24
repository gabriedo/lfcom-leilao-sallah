import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

console.log('Iniciando aplicação...');

try {
  const rootElement = document.getElementById("root");
  if (!rootElement) {
    throw new Error('Elemento root não encontrado!');
  }
  
  console.log('Elemento root encontrado, renderizando aplicação...');
  
  createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
  
  console.log('Aplicação renderizada com sucesso!');
} catch (error) {
  console.error('Erro ao renderizar aplicação:', error);
}
