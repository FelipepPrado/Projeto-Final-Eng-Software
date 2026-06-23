import { useState } from 'react';

// Adicionamos a mesma variável de ambiente que usamos no Cadastro!
const AUTH_API = import.meta.env.VITE_AUTH_API || 'http://localhost:8081';

export default function Login({ onLoginSuccess, aoClicarEmCadastro }) {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setCarregando(true);

    try {
      // Atualizamos a URL para usar a nossa variável dinâmica
      const res = await fetch(`${AUTH_API}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha })
      });

      const data = await res.json();

      if (res.ok) {
        onLoginSuccess(data); // Devolve { id, nome, email } para o App.jsx
      } else {
        setErro(data.erro || 'E-mail ou senha incorretos.');
      }
    } catch (err) {
      setErro('Erro ao tentar conectar com o Auth Service.');
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h2 style={styles.title}>Portal Acadêmico</h2>
          <p style={styles.subtitle}>Acesso restrito</p>
        </div>

        {erro && <div style={styles.errorBanner}>{erro}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>E-mail Institucional</label>
            <input
              type="email"
              required
              placeholder="aluno@ifce.edu.br"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Senha</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              style={styles.input}
            />
          </div>

          <button
            type="submit"
            disabled={carregando}
            style={{
              ...styles.button,
              opacity: carregando ? 0.7 : 1,
              cursor: carregando ? 'wait' : 'pointer'
            }}
          >
            {carregando ? 'Autenticando...' : 'Entrar no Portal'}
          </button>
        </form>

        <div style={styles.footer}>
       <p style={{ color: '#888', fontSize: '12px', margin: '0 0 10px 0' }}>
         Não possui acesso?{' '}
         <button
           type="button"
           onClick={aoClicarEmCadastro}
           style={{ background: 'none', border: 'none', color: '#646cff', cursor: 'pointer', fontWeight: 'bold', padding: 0, textDecoration: 'underline' }}
         >
           Cadastre-se
         </button>
       </p>
       <span style={{ color: '#666', fontSize: '11px' }}>IFCE • Engenharia de Software</span>
     </div>
      </div>
    </div>
  );
}

// Estilos embutidos para garantir que o layout funcione de primeira sem quebrar seu CSS atual
const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    backgroundColor: '#121212',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
  },
  card: {
    backgroundColor: '#1e1e1e',
    padding: '35px 40px',
    borderRadius: '12px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
    width: '100%',
    maxWidth: '360px',
    border: '1px solid #2a2a2a',
    textAlign: 'left',
    boxSizing: 'border-box'
  },
  header: {
    marginBottom: '25px',
    textAlign: 'center',
  },
  title: {
    margin: 0,
    color: '#646cff',
    fontSize: '22px',
  },
  subtitle: {
    margin: '5px 0 0 0',
    color: '#888',
    fontSize: '13px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  label: {
    fontSize: '12px',
    color: '#bbb',
    marginBottom: '6px',
    display: 'block',
    fontWeight: '600',
  },
  input: {
    width: '100%',
    padding: '11px 12px',
    borderRadius: '6px',
    border: '1px solid #383838',
    backgroundColor: '#252525',
    color: '#fff',
    fontSize: '14px',
    boxSizing: 'border-box',
    outline: 'none',
  },
  button: {
    marginTop: '10px',
    padding: '12px',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: '#646cff',
    color: '#fff',
    fontWeight: 'bold',
    fontSize: '14px',
    transition: 'background 0.2s',
  },
  errorBanner: {
    backgroundColor: 'rgba(211, 47, 47, 0.15)',
    color: '#ff6b6b',
    padding: '10px',
    borderRadius: '6px',
    fontSize: '13px',
    marginBottom: '18px',
    textAlign: 'center',
    border: '1px solid rgba(211, 47, 47, 0.3)',
  },
  footer: {
    marginTop: '25px',
    textAlign: 'center',
    borderTop: '1px solid #282828',
    paddingTop: '15px',
  }
};