import { useState } from 'react';

const AUTH_API = import.meta.env.VITE_AUTH_API;

export default function Cadastro({ onCadastroSuccess, aoClicarEmVoltar }) {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [matricula, setMatricula] = useState(''); // <--- ESTADO DA MATRÍCULA
  const [senha, setSenha] = useState('');
  const [tipo, setTipo] = useState('ALUNO');
  
  const [erro, setErro] = useState('');
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro(''); setCarregando(true);

    try {
      const res = await fetch(`${AUTH_API}/api/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, email, matricula, senha, tipo }) // despachando
      });

      const data = await res.json();

      if (res.status === 201) {
        onCadastroSuccess({
          id: data.id,
          nome: data.nome,
          email: data.email,
          tipo: data.tipo,
          matricula: data.matricula // entregando pro App.jsx
        });
      } else if (res.status === 409) setErro('Este e-mail já está cadastrado.');
      else setErro(data.erro || 'Erro ao realizar cadastro.');
    } catch (err) { setErro('Erro de conexão com o Auth Service.'); } 
    finally { setCarregando(false); }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h2 style={styles.title}>Novo Usuário</h2>
          <p style={styles.subtitle}>Crie sua credencial de acesso</p>
        </div>

        {erro && <div style={styles.errorBanner}>{erro}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Nome Completo</label>
            <input type="text" required placeholder="Ex: Carlos Andrade" value={nome} onChange={e => setNome(e.target.value)} style={styles.input} />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>E-mail Institucional</label>
            <input type="email" required placeholder="usuario@ifce.edu.br" value={email} onChange={e => setEmail(e.target.value)} style={styles.input} />
          </div>

          {/* CAMPO INTELIGENTE DA MATRÍCULA */}
          <div style={styles.inputGroup}>
            <label style={styles.label}>
              {tipo === 'ALUNO' ? 'Matrícula Acadêmica' : 'SIAPE / Matrícula Docente'}
            </label>
            <input
              type="text"
              required={tipo === 'ALUNO'} // Obrigatório pra aluno, opcional pra prof!
              placeholder={tipo === 'ALUNO' ? "Ex: 20261045050012" : "Ex: 1234567 (Opcional)"}
              value={matricula}
              onChange={e => setMatricula(e.target.value)}
              style={styles.input}
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Crie uma Senha</label>
            <input type="password" required placeholder="••••••••" value={senha} onChange={e => setSenha(e.target.value)} style={styles.input} />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Perfil de Acesso</label>
            <select value={tipo} onChange={e => setTipo(e.target.value)} style={{ ...styles.input, cursor: 'pointer', borderColor: tipo === 'PROFESSOR' ? '#ffb703' : '#383838' }}>
              <option value="ALUNO">👨‍🎓 Sou Aluno</option>
              <option value="PROFESSOR">👨‍🏫 Sou Professor</option>
            </select>
          </div>

          <button type="submit" disabled={carregando} style={{ ...styles.button, opacity: carregando ? 0.7 : 1, cursor: carregando ? 'wait' : 'pointer' }}>
            {carregando ? 'Registrando...' : 'Cadastrar e Entrar'}
          </button>
        </form>

        <div style={styles.footer}>
          <p style={{ color: '#888', fontSize: '12px', margin: '0 0 10px 0' }}>Já possui conta? <button type="button" onClick={aoClicarEmVoltar} style={styles.link}>Fazer Login</button></p>
          <span style={{ color: '#666', fontSize: '11px' }}>IFCE • Engenharia de Software</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  overlay: { position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: '#121212', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999 },
  card: { backgroundColor: '#1e1e1e', padding: '28px 35px', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.6)', width: '100%', maxWidth: '360px', border: '1px solid #2a2a2a', textAlign: 'left', boxSizing: 'border-box' },
  header: { marginBottom: '18px', textAlign: 'center' },
  title: { margin: 0, color: '#74c69d', fontSize: '22px' }, 
  subtitle: { margin: '5px 0 0 0', color: '#888', fontSize: '13px' },
  form: { display: 'flex', flexDirection: 'column', gap: '11px' },
  inputGroup: { margin: 0 },
  label: { fontSize: '11px', color: '#bbb', marginBottom: '3px', display: 'block', fontWeight: '600' },
  input: { width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #383838', backgroundColor: '#252525', color: '#fff', fontSize: '13px', boxSizing: 'border-box', outline: 'none' },
  button: { marginTop: '6px', padding: '11px', borderRadius: '6px', border: 'none', backgroundColor: '#1b4332', color: '#74c69d', fontWeight: 'bold', fontSize: '14px', transition: 'background 0.2s', border: '1px solid #2d6a4f' },
  errorBanner: { backgroundColor: 'rgba(211, 47, 47, 0.15)', color: '#ff6b6b', padding: '10px', borderRadius: '6px', fontSize: '13px', marginBottom: '14px', textAlign: 'center', border: '1px solid rgba(211, 47, 47, 0.3)' },
  footer: { marginTop: '18px', textAlign: 'center', borderTop: '1px solid #282828', paddingTop: '12px' },
  link: { background: 'none', border: 'none', color: '#646cff', cursor: 'pointer', fontWeight: 'bold', padding: 0, textDecoration: 'underline' }
};