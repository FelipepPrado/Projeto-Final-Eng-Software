import { useState, useEffect } from 'react';

const ASSIGN_API = import.meta.env.VITE_ASSIGN_API || 'http://127.0.0.1:8083';

export default function HomeAluno({ usuario, onLogout }) {
  const [tarefas, setTarefas] = useState([]);
  const [disciplinas, setDisciplinas] = useState([]);
  const [abaAtiva, setAbaAtiva] = useState('TODAS'); // Começa na Visão Geral
  
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState('');

  const buscarMinhasAtividades = async () => {
    setCarregando(true);
    try {
      const res = await fetch(`${ASSIGN_API}/api/assignments/${usuario.id}`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      setTarefas(data.tarefas || []);
      setDisciplinas(data.disciplinas || []);
    } catch (err) {
      setErro('Não foi possível carregar suas turmas.');
    } finally {
      setCarregando(false);
    }
  };

  useEffect(() => { buscarMinhasAtividades(); }, []);

  const handleFinalizar = async (tarefaId) => {
    try {
      const res = await fetch(`${ASSIGN_API}/api/assignments/${tarefaId}/status`, { method: 'PATCH' });
      if (res.ok) buscarMinhasAtividades();
    } catch (err) { alert("Erro ao enviar lição."); }
  };

  // ==========================================
  // 🧠 O MOTOR DE FILTRAGEM INSTANTÂNEA
  // ==========================================
  const tarefasExibidas = abaAtiva === 'TODAS' 
    ? tarefas 
    : tarefas.filter(t => t.disciplina === abaAtiva);

  return (
    <div style={styles.container}>
      
      {/* CABEÇALHO */}
      <header style={styles.header}>
        <div style={{ textAlign: 'left' }}>
          <h2 style={{ margin: 0, color: '#646cff' }}>Portal do Estudante</h2>
          <span style={{ fontSize: '12px', color: '#bbb' }}>
            {usuario.nome} • <b style={{color:'#fff'}}>{usuario.matricula || 'Matrícula Pendente'}</b>
          </span>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={buscarMinhasAtividades} style={styles.btnRefresh}>↻ Atualizar</button>
          <button onClick={onLogout} style={styles.btnLogout}>Sair</button>
        </div>
      </header>

      {carregando ? <p>Carregando sua mochila...</p> : erro ? <p style={{color:'#ff6b6b'}}>{erro}</p> : (
        <>
          {/* ========================================================= */}
          {/* 📑 BARRA DE ABAS DAS MATÉRIAS (Scroll horizontal automático) */}
          {/* ========================================================= */}
          <div style={styles.tabsContainer}>
            <button 
              onClick={() => setAbaAtiva('TODAS')} 
              style={abaAtiva === 'TODAS' ? styles.tabActive : styles.tabInactive}
            >
              📑 Visão Geral ({tarefas.length})
            </button>

            {disciplinas.map(materia => {
              const qtdPendentes = tarefas.filter(t => t.disciplina === materia && t.status !== 'Entregue').length;
              return (
                <button 
                  key={materia} 
                  onClick={() => setAbaAtiva(materia)} 
                  style={abaAtiva === materia ? styles.tabActive : styles.tabInactive}
                >
                  {materia} {qtdPendentes > 0 && <span style={styles.badge}>{qtdPendentes}</span>}
                </button>
              );
            })}
          </div>

          {/* CONTEÚDO DA ABA SELECIONADA */}
          <main style={{ marginTop: '20px' }}>
            {tarefasExibidas.length === 0 ? (
              <div style={styles.emptyState}>
                <h3 style={{ color: '#74c69d', margin: '0 0 5px 0' }}>Nenhuma lição nesta aba!</h3>
                <p style={{ color: '#888', fontSize: '14px', margin: 0 }}>
                  {abaAtiva === 'TODAS' ? 'Sua agenda do semestre está 100% limpa.' : `Você está em dia com as atividades de ${abaAtiva}.`}
                </p>
              </div>
            ) : (
              <div style={styles.tableContainer}>
                <table style={styles.table}>
                  <thead>
                    <tr style={{ background: '#121212', color: '#888', fontSize: '11px', textAlign: 'left' }}>
                      {abaAtiva === 'TODAS' && <th style={{ padding: '14px' }}>DISCIPLINA</th>}
                      <th style={{ padding: '14px' }}>ATIVIDADE</th>
                      <th style={{ padding: '14px', textAlign: 'center' }}>STATUS</th>
                      <th style={{ padding: '14px', textAlign: 'right' }}>AÇÃO</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tarefasExibidas.map(t => (
                      <tr key={t.id} style={{ borderBottom: '1px solid #222', background: t.status === 'Entregue' ? 'rgba(27, 67, 50, 0.25)' : 'transparent' }}>
                        {abaAtiva === 'TODAS' && <td style={{ padding: '16px 14px', fontWeight: 'bold', color: '#646cff' }}>{t.disciplina}</td>}
                        <td style={{ padding: '16px 14px', color: '#fff' }}>{t.titulo}</td>
                        <td style={{ padding: '16px 14px', textAlign: 'center' }}>
                          <span style={{ background: t.status === 'Entregue' ? '#1b4332' : '#7f4f24', color: t.status === 'Entregue' ? '#74c69d' : '#ffb703', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold' }}>
                            {t.status}
                          </span>
                        </td>
                        <td style={{ padding: '16px 14px', textAlign: 'right' }}>
                          {t.status !== 'Entregue' ? (
                            <button onClick={() => handleFinalizar(t.id)} style={styles.btnConcluir}>
                              ✓ Entregar Lição
                            </button>
                          ) : <span style={{ color: '#666', fontSize: '12px' }}>Entregue</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </main>
        </>
      )}
    </div>
  );
}

const styles = {
  container: { maxWidth: '850px', margin: '0 auto', padding: '20px', color: '#fff' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#1f1f1f', padding: '15px 20px', borderRadius: '8px', borderLeft: '5px solid #646cff', marginBottom: '25px' },
  btnRefresh: { background: '#333', color: '#fff', border: '1px solid #444', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' },
  btnLogout: { background: '#d32f2f', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' },
  tabsContainer: { display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '8px', borderBottom: '1px solid #282828' },
  tabInactive: { background: '#1a1a1a', color: '#888', border: '1px solid #282828', padding: '10px 18px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: '600', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '6px' },
  tabActive: { background: '#646cff', color: '#fff', border: '1px solid #747bff', padding: '10px 18px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: 'bold', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '6px', boxShadow: '0 0 12px rgba(100, 108, 255, 0.4)' },
  badge: { background: '#ffb703', color: '#000', fontSize: '10px', fontWeight: '900', padding: '2px 6px', borderRadius: '10px' },
  emptyState: { background: '#1a1a1a', border: '1px dashed #333', borderRadius: '12px', padding: '50px', textAlign: 'center' },
  tableContainer: { background: '#1a1a1a', borderRadius: '10px', overflow: 'hidden', border: '1px solid #282828' },
  table: { width: '100%', borderCollapse: 'collapse', textAlign: 'left' },
  btnConcluir: { background: '#646cff', color: '#fff', border: 'none', padding: '7px 12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontSize: '12px' }
};