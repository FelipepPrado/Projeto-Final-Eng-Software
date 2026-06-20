import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [dados, setDados] = useState(null)
  const [erro, setErro] = useState(null)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    // Faz a requisição para o nosso assignment-service na porta 8083
    fetch('http://localhost:8083/api/assignments/1')
      .then(response => {
        if (!response.ok) throw new Error('Falha ao buscar dados')
        return response.json()
      })
      .then(data => {
        setDados(data)
        setCarregando(false)
      })
      .catch(err => {
        setErro(err.message)
        setCarregando(false)
      })
  }, [])

  if (carregando) return <h2>Carregando plataforma acadêmica...</h2>
  if (erro) return <h2 style={{ color: 'red' }}>Erro: {erro}</h2>

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Plataforma de Gerenciamento Acadêmico</h1>
      
      {dados && (
        <>
          <div style={{ background: '#f4f4f4', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
            <h3>Bem-vindo(a), {dados.aluno}</h3>
            <p><strong>Email:</strong> {dados.email}</p>
          </div>

          <h2>Suas Tarefas:</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
            <thead>
              <tr style={{ background: '#ddd', textAlign: 'left' }}>
                <th style={{ padding: '10px', border: '1px solid #ccc' }}>Disciplina</th>
                <th style={{ padding: '10px', border: '1px solid #ccc' }}>Título</th>
                <th style={{ padding: '10px', border: '1px solid #ccc' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {dados.tarefas.map((tarefa, index) => (
                <tr key={index}>
                  <td style={{ padding: '10px', border: '1px solid #ccc' }}>{tarefa.disciplina}</td>
                  <td style={{ padding: '10px', border: '1px solid #ccc' }}>{tarefa.titulo}</td>
                  <td style={{ padding: '10px', border: '1px solid #ccc' }}>
                    <span style={{ 
                      background: tarefa.status === 'Entregue' ? '#d4edda' : '#fff3cd',
                      color: tarefa.status === 'Entregue' ? '#155724' : '#856404',
                      padding: '5px 10px', borderRadius: '5px', fontWeight: 'bold'
                    }}>
                      {tarefa.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}

export default App