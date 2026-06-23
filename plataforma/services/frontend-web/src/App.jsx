import { useState, useEffect } from 'react';
import Login from './components/Login';
import Cadastro from './components/Cadastro';
import HomeProfessor from './components/HomeProfessor';
import HomeAluno from './components/HomeAluno';
import './App.css';

function App() {
  const [usuarioLogado, setUsuarioLogado] = useState(null);
  const [abaExterna, setAbaExterna] = useState('login'); // 'login' ou 'cadastro'

  // Mantém o usuário logado se ele der F5
  useEffect(() => {
    const salvo = localStorage.getItem('usuario');
    if (salvo) setUsuarioLogado(JSON.parse(salvo));
  }, []);

  const handleEntrouNoSistema = (dadosUsuario) => {
    setUsuarioLogado(dadosUsuario);
    localStorage.setItem('usuario', JSON.stringify(dadosUsuario));
  };

  const handleSairDoSistema = () => {
    localStorage.removeItem('usuario');
    setUsuarioLogado(null);
  };

  // ==========================================
  // 🚦 ROTEAMENTO SPA (O interruptor)
  // ==========================================

  // 1. Se não tá logado, mostra a portaria (Login ou Cadastro)
  if (!usuarioLogado) {
    if (abaExterna === 'cadastro') {
      return <Cadastro onCadastroSuccess={handleEntrouNoSistema} aoClicarEmVoltar={() => setAbaExterna('login')} />;
    }
    return <Login onLoginSuccess={handleEntrouNoSistema} aoClicarEmCadastro={() => setAbaExterna('cadastro')} />;
  }

  // 2. Tá logado e o crachá diz PROFESSOR? Joga na Home do Professor.
  if (usuarioLogado.tipo === 'PROFESSOR') {
    return <HomeProfessor usuario={usuarioLogado} onLogout={handleSairDoSistema} />;
  }

  // 3. Se passou pelos dois IFs acima, com certeza é um ALUNO. Joga na Home do Aluno.
  return <HomeAluno usuario={usuarioLogado} onLogout={handleSairDoSistema} />;
}

export default App;