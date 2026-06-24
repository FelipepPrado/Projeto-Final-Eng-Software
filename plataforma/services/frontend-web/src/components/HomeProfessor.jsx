import { useState, useEffect } from 'react';

const ACADEMIC_API = import.meta.env.VITE_ACADEMIC_API;
const ASSIGN_API   = import.meta.env.VITE_ASSIGN_API;

export default function HomeProfessor({ usuario, onLogout }) {
  const [minhasDisciplinas, setMinhasDisciplinas] = useState([]);

  const [nomeNovaDisciplina, setNomeNovaDisciplina] = useState('');
  const [msgDiscSucesso,     setMsgDiscSucesso]     = useState('');

  const [vincularDiscId,    setVincularDiscId]    = useState('');
  const [vincularMatricula, setVincularMatricula] = useState('');
  const [msgVincSucesso,    setMsgVincSucesso]    = useState('');

  const [tarefaDiscId,     setTarefaDiscId]     = useState('');
  const [tarefaTitulo,     setTarefaTitulo]     = useState('');
  const [msgTarefaSucesso, setMsgTarefaSucesso] = useState('');

  const [erroGeral,  setErroGeral]  = useState('');
  const [carregando, setCarregando] = useState(false);

  const buscarDisciplinas = async () => {
    try {
      const res = await fetch(`${ACADEMIC_API}/api/academic/subjects/professor/${usuario.id}`);
      if (res.ok) {
        const data = await res.json();
        setMinhasDisciplinas(data);
        if (data.length > 0) {
          if (!vincularDiscId) setVincularDiscId(data[0].id.toString());
          if (!tarefaDiscId)   setTarefaDiscId(data[0].id.toString());
        }
      }
    } catch (err) { console.error('Erro ao buscar disciplinas:', err); }
  };

  useEffect(() => { buscarDisciplinas(); }, []);

  const limparAvisos = () => {
    setErroGeral(''); setMsgDiscSucesso(''); setMsgVincSucesso(''); setMsgTarefaSucesso('');
  };

  const handleCriarDisciplina = async (e) => {
    e.preventDefault(); limparAvisos(); setCarregando(true);
    try {
      const res = await fetch(`${ACADEMIC_API}/api/academic/subjects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: nomeNovaDisciplina, professor_id: usuario.id })
      });
      const data = await res.json();
      if (res.status === 201) { setMsgDiscSucesso(`Disciplina '${data.nome}' criada com sucesso!`); setNomeNovaDisciplina(''); buscarDisciplinas(); }
      else setErroGeral(data.erro);
    } catch { setErroGeral('Erro de rede ao criar disciplina.'); }
    finally { setCarregando(false); }
  };

  const handleMatricularAluno = async (e) => {
    e.preventDefault(); limparAvisos(); setCarregando(true);
    try {
      const res = await fetch(`${ACADEMIC_API}/api/academic/enroll`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ disciplina_id: vincularDiscId, matricula: vincularMatricula })
      });
      const data = await res.json();
      if (res.status === 201) { setMsgVincSucesso(data.mensagem); setVincularMatricula(''); }
      else setErroGeral(data.erro);
    } catch { setErroGeral('Erro de rede ao matricular aluno.'); }
    finally { setCarregando(false); }
  };

  const handleDispararAtividade = async (e) => {
    e.preventDefault(); limparAvisos(); setCarregando(true);
    const discSelecionada = minhasDisciplinas.find(d => d.id.toString() === tarefaDiscId);
    if (!discSelecionada) { setErroGeral('Selecione uma disciplina válida.'); setCarregando(false); return; }
    try {
      const res = await fetch(`${ASSIGN_API}/api/assignments/broadcast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ disciplina_id: tarefaDiscId, disciplina_nome: discSelecionada.nome, titulo: tarefaTitulo })
      });
      const data = await res.json();
      if (res.status === 201) { setMsgTarefaSucesso(data.mensagem); setTarefaTitulo(''); }
      else setErroGeral(data.erro);
    } catch { setErroGeral('Erro de rede ao disparar atividade.'); }
    finally { setCarregando(false); }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div>
          <h2 style={{ margin: 0, color: '#ffb703' }}>Painel Docente</h2>
          <span style={{ fontSize: '12px', color: '#bbb' }}>Prof. {usuario.nome}</span>
        </div>
        <button onClick={onLogout} style={styles.btnLogout}>Sair</button>
      </header>

      {erroGeral && <div style={styles.bannerErro}>{erroGeral}</div>}

      <div style={styles.grid}>
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>1. Criar Disciplina</h3>
          {msgDiscSucesso && <div style={styles.bannerSucesso}>{msgDiscSucesso}</div>}
          <form onSubmit={handleCriarDisciplina} style={styles.form}>
            <div>
              <label style={styles.label}>Nome da matéria</label>
              <input type="text" required placeholder="Ex: Algoritmos" value={nomeNovaDisciplina} onChange={e => setNomeNovaDisciplina(e.target.value)} style={styles.input} />
            </div>
            <button type="submit" disabled={carregando} style={styles.btnSubmit}>Criar Turma</button>
          </form>
        </div>

        <div style={styles.card}>
          <h3 style={styles.cardTitle}>2. Matricular Aluno</h3>
          {msgVincSucesso && <div style={styles.bannerSucesso}>{msgVincSucesso}</div>}
          <form onSubmit={handleMatricularAluno} style={styles.form}>
            <div>
              <label style={styles.label}>Turma</label>
              <select value={vincularDiscId} onChange={e => setVincularDiscId(e.target.value)} style={styles.input} disabled={minhasDisciplinas.length === 0}>
                {minhasDisciplinas.length === 0
                  ? <option>Nenhuma turma criada</option>
                  : minhasDisciplinas.map(d => <option key={d.id} value={d.id}>{d.nome}</option>)
                }
              </select>
            </div>
            <div>
              <label style={styles.label}>Matrícula Acadêmica do Aluno</label>
              <input type="text" required placeholder="Ex: 20261045050012" value={vincularMatricula} onChange={e => setVincularMatricula(e.target.value)} style={styles.input} />
            </div>
            <button type="submit" disabled={carregando || minhasDisciplinas.length === 0} style={styles.btnSubmit}>Matricular na Sala</button>
          </form>
        </div>
      </div>

      <div style={{ ...styles.card, marginTop: '20px' }}>
        <h3 style={styles.cardTitle}>3. Disparar Atividade para a Turma</h3>
        {msgTarefaSucesso && <div style={styles.bannerSucesso}>{msgTarefaSucesso}</div>}
        <form onSubmit={handleDispararAtividade} style={{ display: 'flex', gap: '15px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label style={styles.label}>Turma Destino</label>
            <select value={tarefaDiscId} onChange={e => setTarefaDiscId(e.target.value)} style={styles.input} disabled={minhasDisciplinas.length === 0}>
              {minhasDisciplinas.map(d => <option key={d.id} value={d.id}>{d.nome}</option>)}
            </select>
          </div>
          <div style={{ flex: 2 }}>
            <label style={styles.label}>Tarefa</label>
            <input type="text" required placeholder="Ex: Ler o capítulo 3" value={tarefaTitulo} onChange={e => setTarefaTitulo(e.target.value)} style={styles.input} />
          </div>
          <button type="submit" disabled={carregando || minhasDisciplinas.length === 0} style={{ ...styles.btnSubmit, width: 'auto', padding: '10px 25px' }}>Disparar</button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  container:     { maxWidth: '850px', margin: '0 auto', padding: '20px', textAlign: 'left', color: '#fff' },
  header:        { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1f1f1f', padding: '15px 20px', borderRadius: '8px', borderLeft: '5px solid #ffb703', marginBottom: '25px' },
  btnLogout:     { background: '#d32f2f', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' },
  grid:          { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' },
  card:          { background: '#1e1e1e', border: '1px solid #2a2a2a', borderRadius: '10px', padding: '22px', boxShadow: '0 4px 15px rgba(0,0,0,0.4)', boxSizing: 'border-box' },
  cardTitle:     { marginTop: 0, color: '#ffb703', borderBottom: '1px solid #333', paddingBottom: '8px', fontSize: '16px' },
  form:          { display: 'flex', flexDirection: 'column', gap: '14px' },
  label:         { fontSize: '12px', color: '#bbb', marginBottom: '4px', display: 'block', fontWeight: '600' },
  input:         { width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #333', background: '#252525', color: '#fff', boxSizing: 'border-box', outline: 'none' },
  btnSubmit:     { padding: '11px', background: '#ffb703', color: '#000', fontWeight: 'bold', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  bannerSucesso: { background: 'rgba(116, 198, 157, 0.15)', color: '#74c69d', padding: '10px', borderRadius: '6px', marginBottom: '15px', border: '1px solid #2d6a4f', fontSize: '13px' },
  bannerErro:    { background: 'rgba(211, 47, 47, 0.15)', color: '#ff6b6b', padding: '10px', borderRadius: '6px', marginBottom: '15px', border: '1px solid rgba(211, 47, 47, 0.3)', fontSize: '13px' }
};