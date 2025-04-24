import React from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Dashboard from "./pages/Dashboard";
import NovaAnalise from "./pages/NovaAnalise";
import PropertyReportPage from "./pages/PropertyReportPage";
import Sobre from "./pages/Sobre";
import NotFound from "./pages/NotFound";
import ComoFunciona from "./pages/ComoFunciona";
import Precos from "./pages/Precos";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import FAQ from "./pages/FAQ";
import ImoveisCaixa from "./pages/ImoveisCaixa";
import PropertyDetails from "./pages/PropertyDetails";
import Conteudos from "./pages/Conteudos";
import ConteudoDetalhe from "./pages/ConteudoDetalhe";
import Assessoria from "./pages/Assessoria";
import Contato from "./pages/Contato";
import MeuPlano from "./pages/MeuPlano";
import LeiloeirosPagina from "./pages/LeiloeirosPagina";
import Ajuda from "./pages/Ajuda";
import Termos from "./pages/Termos";
import Privacidade from "./pages/Privacidade";
import Recursos from "./pages/Recursos";
import ConhecerMetodologia from "./pages/ConhecerMetodologia";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";

const queryClient = new QueryClient();

function App() {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter future={{ v7_startTransition: true }}>
          <AuthProvider>
            <Toaster />
            <Sonner />
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/nova-analise" element={<ProtectedRoute><NovaAnalise /></ProtectedRoute>} />
              <Route path="/meu-plano" element={<ProtectedRoute><MeuPlano /></ProtectedRoute>} />
              <Route path="/imoveis-caixa" element={<ImoveisCaixa />} />
              <Route path="/imoveis-caixa/:id" element={<PropertyDetails />} />
              <Route path="/imovel/:id" element={<PropertyDetails />} />
              <Route path="/relatorio/:id" element={<PropertyReportPage />} />
              <Route path="/conteudos" element={<Conteudos />} />
              <Route path="/conteudos/:id" element={<ConteudoDetalhe />} />
              <Route path="/como-funciona" element={<ComoFunciona />} />
              <Route path="/conhecer-metodologia" element={<ConhecerMetodologia />} />
              <Route path="/assessoria" element={<Assessoria />} />
              <Route path="/contato" element={<Contato />} />
              <Route path="/precos" element={<Precos />} />
              <Route path="/leiloeiros" element={<LeiloeirosPagina />} />
              <Route path="/perfil" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/faq" element={<FAQ />} />
              <Route path="/sobre" element={<Sobre />} />
              <Route path="/ajuda" element={<Ajuda />} />
              <Route path="/termos" element={<Termos />} />
              <Route path="/privacidade" element={<Privacidade />} />
              <Route path="/recursos" element={<Recursos />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </React.StrictMode>
  );
}

export default App;
