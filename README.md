# Autenticação Microsoft IBMEC com Perfis

Projeto para autenticação com contas Microsoft do IBMEC com diferentes perfis (Professor e Aluno).

## Funcionalidades

- Autenticação com contas Microsoft existentes do IBMEC
- Detecção automática de perfil baseada no email:
  - Se o email contiver "professor", o usuário terá perfil de Professor
  - Caso contrário, o usuário terá perfil de Aluno
- Dashboards específicos para cada perfil de usuário
- Interface personalizada de acordo com o perfil

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Configuração Microsoft

1. Registre seu aplicativo no [Portal Azure](https://portal.azure.com)
2. Configure o aplicativo como multilocatário
3. Adicione o URI de redirecionamento: `http://localhost:8000/auth/callback`
4. Adicione as credenciais obtidas ao arquivo `.env` no backend

## Como testar

Para testar os diferentes perfis:

1. Faça login com um email que contenha "professor" (ex: professor.silva@ibmec.edu.br)
2. Observe o dashboard do Professor com sua interface específica
3. Faça logout e faça login novamente com um email que não contenha "professor" 
4. Observe o dashboard do Aluno com sua interface específica
