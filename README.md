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



# Passo a Passo para Configurar o Aplicativo no Azure

Aqui está um guia detalhado para configurar seu aplicativo de autenticação Microsoft no Azure:

## 1. Criar uma Conta no Azure

Se você ainda não tiver uma conta no Azure:
1. Acesse [portal.azure.com](https://portal.azure.com)
2. Clique em "Criar uma conta gratuita"
3. Siga as instruções para criar sua conta (talvez precise fornecer um cartão de crédito, mas não haverá cobrança para o nível gratuito)

## 2. Registrar um Novo Aplicativo

1. Após fazer login no [Portal Azure](https://portal.azure.com), clique no menu ☰ no canto superior esquerdo
2. Busque por "Microsoft Entra ID" (antigo Azure Active Directory) e selecione-o
3. No painel lateral esquerdo, clique em "Registros de aplicativo"
4. Clique no botão "+ Novo registro" no topo da página
5. Preencha os detalhes do aplicativo:
   * **Nome**: "IBMEC Auth" ou outro nome de sua preferência
   * **Tipos de conta com suporte**: Selecione "Contas em qualquer diretório organizacional (Qualquer diretório do Microsoft Entra ID - Multilocatário)"
   * **URI de redirecionamento (opcional)**:
      * Plataforma: Web
      * URL: `http://localhost:8000/auth/callback` (para desenvolvimento)
6. Clique em "Registrar"

## 3. Anotar as Credenciais do Aplicativo

Após o registro, você estará na página de visão geral do aplicativo:

1. Anote o **ID do aplicativo (cliente)** - você precisará dele para o arquivo .env
2. Anote o **ID do diretório (locatário)** - embora usaremos "common" para multilocatário

## 4. Criar um Segredo do Cliente (Client Secret)

1. No menu lateral esquerdo da página do seu aplicativo, clique em "Certificados e segredos"
2. Na seção "Segredos do cliente", clique em "+ Novo segredo do cliente"
3. Adicione uma descrição (ex: "Chave de Desenvolvimento") e escolha um período de validade
4. Clique em "Adicionar"
5. **IMPORTANTE**: Copie o **Valor** do segredo imediatamente. Ele só será exibido uma vez e não poderá ser recuperado depois!

## 5. Configurar Permissões de API

1. No menu lateral esquerdo da página do seu aplicativo, clique em "Permissões de API"
2. Clique em "+ Adicionar uma permissão"
3. Selecione "Microsoft Graph"
4. Selecione "Permissões delegadas"
5. Procure e selecione:
   * User.Read (permite login básico e leitura do perfil do usuário)
   * User.ReadBasic.All (opcional - para obter informações básicas de outros usuários)
6. Clique em "Adicionar permissões"

## 6. Configurar o Arquivo .env no Backend

No diretório "backend" do seu projeto, edite o arquivo `.env` com as seguintes informações:

```
SECRET_KEY=sua-chave-secreta-aqui-pode-ser-qualquer-string-longa
MS_TENANT_ID=common
MS_CLIENT_ID=seu-id-do-aplicativo-que-voce-anotou
MS_CLIENT_SECRET=seu-segredo-do-cliente-que-voce-anotou
MS_REDIRECT_URI=http://localhost:8000/auth/callback
FRONTEND_URL=http://localhost:3000
```

## 7. Iniciar o Projeto

### Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm start
```

## 8. Testar a Autenticação

1. Acesse `http://localhost:3000` no navegador
2. Clique no botão "Entrar com Microsoft"
3. Você será redirecionado para a página de login da Microsoft
4. Faça login com sua conta do IBMEC (@ibmec.edu.br)
5. Na primeira vez, a Microsoft pedirá que você autorize o acesso do aplicativo
6. Após a autorização, você será redirecionado de volta para o aplicativo, já autenticado

### Para testar os diferentes perfis:
* Use uma conta com "professor" no email para acessar o dashboard de Professor
* Use uma conta sem "professor" no email para acessar o dashboard de Aluno

## 9. Para Configurar em Produção

Quando estiver pronto para implantar em produção:

1. Adicione novos URIs de redirecionamento no registro do aplicativo:
   * No registro do aplicativo, vá para "Autenticação"
   * Adicione o novo URI: `https://seu-dominio.com/auth/callback`

2. Atualize o arquivo `.env` em produção:
```
MS_REDIRECT_URI=https://seu-dominio.com/auth/callback
FRONTEND_URL=https://seu-dominio.com
```

3. Configure HTTPS para ambos backend e frontend
4. Considere usar um gerenciador de segredos para armazenar as credenciais em produção