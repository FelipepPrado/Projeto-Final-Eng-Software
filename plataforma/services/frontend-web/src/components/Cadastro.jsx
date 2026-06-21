import { useState } from 'react';

export default function Cadastro({ onCadastroSuccess, aoClicarEmVoltar }) {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setCarregando(true);

    try {
      const res = await fetch('http://127.0.0.1:8081/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, email, senha })
      });

      const data = await res.json();

      if (res.status === 201) {
        // MÁGICA DE UX: Se cadastrou com sucesso, já logamos ele direto!
        onCadastroSuccess({
          id: data.id,
          nome: data.nome,
          email: data.email
        });
      } else if (res.status === 409) {
        setErro('Este e-mail já está cadastrado no sistema.');
      } else {
        setErro(data.erro || 'Erro ao realizar cadastro.');
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
          <h2 style={styles.title}>Novo Aluno</h2>
          <p style={styles.subtitle}>Crie sua credencial de acesso</p>
        </div>

        {erro && <div style={styles.errorBanner}>{erro}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Nome Completo</label>
            <input
              type="text"
              required
              placeholder="Ex: Carlos Andrade"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              style={styles.input}
            />
          </div>

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
            <label style={styles.label}>Crie uma Senha</label>
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
            {carregando ? 'Registrando...' : 'Cadastrar e Entrar'}
          </button>
        </form>

        <div style={styles.footer}>
          <p style={{ color: '#888', fontSize: '12px', margin: '0 0 10px 0' }}>
            Já possui uma conta?{' '}
            <button
              type="button"
              onClick={aoClicarEmVoltar}
              style={{ background: 'none', border: 'none', color: '#646cff', cursor: 'pointer', fontWeight: 'bold', padding: 0, textDecoration: 'underline' }}
            >
              Fazer Login
            </button>
          </p>
          <span style={{ color: '#666', fontSize: '11px' }}>IFCE • Engenharia de Software</span>
        </div>
      </div>
    </div>
  );
}

// Estilos espelhados do Login para manter a identidade visual 100% uniforme
const styles = {
  overlay: { position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: '#121212', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999 },
  card: { backgroundColor: '#1e1e1e', padding: '35px 40px', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.6)', width: '100%', maxWidth: '360px', border: '1px solid #2a2a2a', textAlign: 'left', boxSizing: 'border-box' },
  header: { marginBottom: '25px', textAlign: 'center' },
  title: { margin: 0, color: '#74c69d', fontSize: '22px' }, // Tom esverdeado para diferenciar da tela de login
  subtitle: { margin: '5px 0 0 0', color: '#888', fontSize: '13px' },
  form: { display: 'flex', flexDirection: 'column', gap: '14px' },
  label: { fontSize: '12px', color: '#bbb', marginBottom: '4px', display: 'block', fontWeight: '600' },
  input: { width: '100%', padding: '10px 12px', borderRadius: '6px', border: '1px solid #383838', backgroundColor: '#252525', color: '#fff', fontSize: '14px', boxSizing: 'border-box', outline: 'none' },
  button: { marginTop: '10px', padding: '12px', borderRadius: '6px', border: 'none', backgroundColor: '#1b4332', color: '#74c69d', fontWeight: 'bold', fontSize: '14px', transition: 'background 0.2s', border: '1px solid #2d6a4f' },
  errorBanner: { backgroundColor: 'rgba(211, 47, 47, 0.15)', color: '#ff6b6b', padding: '10px', borderRadius: '6px', fontSize: '13px', marginBottom: '18px', textAlign: 'center', border: '1px solid rgba(211, 47, 47, 0.3)' },
  footer: { marginTop: '25px', textAlign: 'center', borderTop: '1px solid #282828', paddingTop: '15px' }
};