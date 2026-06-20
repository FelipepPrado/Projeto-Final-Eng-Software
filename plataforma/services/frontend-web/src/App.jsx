import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // Controle do Aluno logado/visualizado
  const [alunoIdAtivo, setAlunoIdAtivo] = useState(1)
  const [inputBuscaId, setInputBuscaId] = useState('1')
  const [dados, setDados] = useState(null)
  const [carregando, setCarregando] = useState(true)

  // Form: Nova Pessoa
  const [novoNome, setNovoNome] = useState('')
  const [novoEmail, setNovoEmail] = useState('')

  // Form: Nova Tarefa
  const [novaDisciplina, setNovaDisciplina] = useState('')
  const [novoTitulo, setNovoTitulo] = useState('')

  const buscarDadosDoAluno = (id) => {
    setCarregando(true)
    fetch(`http://localhost:8083/api/assignments/${id}`)
      .then(res => {
        if (!res.ok) throw new Error('Usuário não encontrado')
        return res.json()
      })
      .then(data => { setDados(data); setCarregando(false) })
      .catch(() => { setDados(null); setCarregando(false) })
  }

  // Busca os dados sempre que o ID ativo mudar
  useEffect(() => { buscarDadosDoAluno(alunoIdAtivo) }, [alunoIdAtivo])

  const handleCriarPessoa = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch('http://localhost:8081/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: novoNome, email: novoEmail })
      })
      const data = await res.json()
      
      if (res.ok) {
        alert(`Sucesso! ${data.nome} foi cadastrado(a) com o ID: ${data.id}`)
        setNovoNome(''); setNovoEmail('')
        setAlunoIdAtivo(data.id)
        setInputBuscaId(data.id.toString())
      } else if (res.status === 409) { // <--- AQUI TRATAMOS O WARNING
        alert("Atenção: " + data.erro)
      } else {
        alert("Erro: " + data.erro)
      }
    } catch (err) { alert('Erro ao conectar com Auth Service') }
  }

  // Dispara o POST para o Assignment Service
  const handleCriarTarefa = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch('http://localhost:8083/api/assignments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          aluno_id: parseInt(alunoIdAtivo),
          disciplina: novaDisciplina,
          titulo: novoTitulo
        })
      })
      if (res.ok) {
        setNovaDisciplina(''); setNovoTitulo('')
        buscarDadosDoAluno(alunoIdAtivo) 
      } else alert('Erro ao criar tarefa')
    } catch (err) { alert('Erro ao conectar com Assignment Service') }
  }
  
  const mudarStatus = async (tarefaId) => {
    try {
      const resposta = await fetch(`http://localhost:8083/api/assignments/${tarefaId}/status`, {
        method: 'PATCH'
      });
      
      if (resposta.ok) {
        buscarDadosDoAluno(alunoIdAtivo); 
      }
    } catch (error) {
      console.error("Erro ao atualizar status:", error);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '900px', margin: '0 auto' }}>
      
      {/* BARRA SUPERIOR: TROCAR DE ALUNO */}
      <div style={{ background: '#1f1f1f', padding: '10px 20px', borderRadius: '8px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0, color: '#646cff' }}>Portal Acadêmico</h3>
        <div>
          <label style={{ fontSize: '14px', marginRight: '8px',color:'#FFFFFF' }}>Visualizar Aluno (ID):</label>
          <input 
            type="number" 
            value={inputBuscaId} 
            onChange={(e) => setInputBuscaId(e.target.value)}
            style={{ width: '50px', padding: '4px', borderRadius: '4px', border: '1px solid #555', background: '#333', color: '#FFFFFF' }}
          />
          <button 
            onClick={() => setAlunoIdAtivo(parseInt(inputBuscaId))}
            style={{ marginLeft: '8px', padding: '5px 12px', background: '#646cff', border: 'none', borderRadius: '4px', color: '#fff', cursor: 'pointer' }}>
            Buscar
          </button>
        </div>
      </div>

      {/* ÁREA CENTRAL: DADOS DO ALUNO ATIVO */}
      {carregando ? ( <h4 style={{ color: '#ffffff' }}>Carregando registros...</h4> ) : dados ? (
        <>
          <div style={{ background: '#242424', color: '#ffffff', padding: '15px', borderRadius: '8px', marginBottom: '20px', borderLeft: '4px solid #646cff', textAlign: 'left' }}>
            <h2 style={{ margin: '0 0 5px 0', color: '#ffffff' }}>{dados.aluno} <span style={{ fontSize:'12px', color:'#aaaaaa' }}>(ID: {alunoIdAtivo})</span></h2>
            <p style={{ margin: 0, color: '#dddddd' }}>E-mail: {dados.email}</p>
          </div>

          <h3 style={{ textAlign: 'left', borderBottom: '1px solid #444', paddingBottom: '5px', color: '#ffffff' }}>Tarefas Atribuídas:</h3>
          {dados.tarefas.length === 0 ? (<p style={{ color: '#aaaaaa', textAlign: 'left' }}>Nenhuma tarefa cadastrada para este aluno ainda.</p>) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '30px', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: '#1a1a1a', color: '#ffffff' }}>
                  <th style={{ padding: '10px', borderBottom: '1px solid #333' }}>Disciplina</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid #333' }}>Atividade</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid #333', textAlign:'center' }}>Status</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid #333', textAlign:'center' }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {dados.tarefas.map((t, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #222' }}>
                    <td style={{ padding: '10px' }}>{t.disciplina}</td>
                    <td style={{ padding: '10px' }}>{t.titulo}</td>
                    <td style={{ padding: '10px', textAlign:'center' }}>
                      <span style={{ background: '#7f4f24', color: '#ffb703', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold' }}>
                        {t.status}
                      </span>
                    </td>
                    <td style={{ padding: '10px', textAlign:'center' }}>
                      {t.status !== 'Entregue' && (
                        <button 
                          onClick={() => mudarStatus(t.id)} 
                          style={{ background: '#646cff', color: '#fff', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}>
                          Entregar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      ) : ( 
        <div style={{ padding: '30px', background: '#331313', borderRadius: '8px', marginBottom:'20px', color:'#f8aba6' }}>
          <h3>Nenhum Aluno encontrado com o ID "{alunoIdAtivo}"</h3>
          <p>Utilize o formulário abaixo para criar uma nova pessoa no banco de dados.</p>
        </div> 
      )}

      {/* RODAPÉ: OS DOIS FORMULÁRIOS DE CADASTRO */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '40px', textAlign: 'left' }}>
        
        {/* FORM 1 */}
        <form onSubmit={handleCriarPessoa} style={{ background: '#1a1a1a', color: '#ffffff', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>
          <h4 style={{ margin: '0 0 15px 0', color: '#74c69d' }}>+ Cadastrar Nova Pessoa</h4>
          <input required placeholder="Nome Completo" value={novoNome} onChange={e => setNovoNome(e.target.value)} style={{ width: '100%', marginBottom: '10px', padding: '8px', boxSizing:'border-box', background:'#222', border:'1px solid #444', color:'#ffffff', borderRadius:'4px' }} />
          <input required type="email" placeholder="E-mail" value={novoEmail} onChange={e => setNovoEmail(e.target.value)} style={{ width: '100%', marginBottom: '15px', padding: '8px', boxSizing:'border-box', background:'#222', border:'1px solid #444', color:'#ffffff', borderRadius:'4px' }} />
          <button type="submit" style={{ width: '100%', padding: '10px', background: '#1b4332', color: '#74c69d', fontWeight:'bold', border:'none', borderRadius:'4px', cursor:'pointer' }}>Criar Pessoa</button>
        </form>

        {/* FORM 2 */}
        <form onSubmit={handleCriarTarefa} style={{ background: '#1a1a1a', color: '#ffffff', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>
          <h4 style={{ margin: '0 0 15px 0', color: '#ffb703' }}>+ Atribuir Tarefa ao ID ({alunoIdAtivo})</h4>
          <input required placeholder="Nome da Disciplina" value={novaDisciplina} onChange={e => setNovaDisciplina(e.target.value)} style={{ width: '100%', marginBottom: '10px', padding: '8px', boxSizing:'border-box', background:'#222', border:'1px solid #444', color:'#ffffff', borderRadius:'4px' }} />
          <input required placeholder="Título / Descrição da Atividade" value={novoTitulo} onChange={e => setNovoTitulo(e.target.value)} style={{ width: '100%', marginBottom: '15px', padding: '8px', boxSizing:'border-box', background:'#222', border:'1px solid #444', color:'#ffffff', borderRadius:'4px' }} />
          <button type="submit" disabled={!dados} style={{ width: '100%', padding: '10px', background: dados ? '#7f4f24' : '#333', color: dados ? '#ffb703' : '#666', fontWeight:'bold', border:'none', borderRadius:'4px', cursor: dados ? 'pointer' : 'not-allowed' }}>Adicionar Tarefa</button>
        </form>
      </div>
    </div>
  )
}

export default App