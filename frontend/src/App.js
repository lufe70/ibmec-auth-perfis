// src/App.js - Atualizado para diferentes perfis
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Componente de Login
function LoginPage() {
  const handleLogin = () => {
    window.location.href = `${API_URL}/auth/login`;
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>Login IBMEC</h1>
        <p>Faça login com sua conta institucional do IBMEC</p>
        <button className="login-button" onClick={handleLogin}>
          <svg className="ms-logo" viewBox="0 0 23 23" xmlns="http://www.w3.org/2000/svg">
            <path fill="#f25022" d="M1 1h10v10H1z" />
            <path fill="#00a4ef" d="M1 12h10v10H1z" />
            <path fill="#7fba00" d="M12 1h10v10H12z" />
            <path fill="#ffb900" d="M12 12h10v10H12z" />
          </svg>
          Entrar com Microsoft
        </button>
      </div>
    </div>
  );
}

// Componente para processar o retorno da autenticação
function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const token = urlParams.get('token');
    
    if (token) {
      localStorage.setItem('auth_token', token);
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  }, [location, navigate]);
  
  return (
    <div className="auth-callback">
      <p>Processando autenticação...</p>
    </div>
  );
}

// Componente Dashboard para usuários autenticados
function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        navigate('/login');
        return;
      }
      
      try {
        const response = await fetch(`${API_URL}/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Token inválido
          localStorage.removeItem('auth_token');
          navigate('/login');
        }
      } catch (error) {
        console.error('Erro ao buscar dados do usuário:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUserData();
  }, [navigate]);
  
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    navigate('/login');
  };
  
  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  // Renderização condicional baseada no perfil (role)
  return (
    <div className="dashboard">
      <header className={`header-${user.role}`}>
        <h1>Dashboard IBMEC - {user.role === 'professor' ? 'Professor' : 'Aluno'}</h1>
        <button className="logout-button" onClick={handleLogout}>Sair</button>
      </header>
      
      <div className="user-info">
        <h2>Bem-vindo, {user?.name || user?.username}</h2>
        <div className="user-details">
          <p><strong>Email:</strong> {user?.email}</p>
          <p><strong>Nome de usuário:</strong> {user?.username}</p>
          <p><strong>Perfil:</strong> {user?.role === 'professor' ? 'Professor' : 'Aluno'}</p>
        </div>
      </div>
      
      {user?.role === 'professor' ? (
        <div className="professor-dashboard">
          <h3>Painel de Professor</h3>
          <div className="features-container">
            <div className="feature-card">
              <h4>Gerenciamento de Turmas</h4>
              <p>Acesse as turmas, configure avaliações e monitore o desempenho dos alunos.</p>
            </div>
            <div className="feature-card">
              <h4>Material Didático</h4>
              <p>Faça upload de materiais para suas disciplinas e organize o conteúdo.</p>
            </div>
            <div className="feature-card">
              <h4>Calendário Acadêmico</h4>
              <p>Visualize e gerencie datas importantes e horários de aulas.</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="aluno-dashboard">
          <h3>Painel de Aluno</h3>
          <div className="features-container">
            <div className="feature-card">
              <h4>Minhas Disciplinas</h4>
              <p>Acesse suas disciplinas, materiais de aula e atividades.</p>
            </div>
            <div className="feature-card">
              <h4>Notas e Frequência</h4>
              <p>Consulte seu desempenho acadêmico e presença nas aulas.</p>
            </div>
            <div className="feature-card">
              <h4>Horários</h4>
              <p>Visualize sua grade horária semanal e calendário de provas.</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="auth-success">
        <h3>Autenticação Microsoft bem-sucedida!</h3>
        <p>Você está conectado com sua conta IBMEC como {user?.role === 'professor' ? 'Professor' : 'Aluno'}.</p>
      </div>
    </div>
  );
}

// Componente para verificar autenticação nas rotas
function RequireAuth({ children }) {
  const isAuthenticated = localStorage.getItem('auth_token') !== null;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
}

// Aplicação principal
function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth" element={<AuthCallback />} />
          <Route 
            path="/dashboard" 
            element={
              <RequireAuth>
                <Dashboard />
              </RequireAuth>
            } 
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
