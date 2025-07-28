# Planejamento de Desenvolvimento - Checklist App

## Informações do Projeto

### Tecnologias
- **Frontend**: Next.js + React + Shadcn/UI + Tailwind CSS (sem TypeScript)
- **Backend**: FastAPI + PostgreSQL + Alembic + SQLAlchemy
- **Autenticação**: OAuth 2.0 Google

### Funcionalidades Principais
- Login com conta Google
- Dashboard com listagem de checklists
- Criação, edição e exclusão de checklists
- Gerenciamento de itens dentro dos checklists
- Marcação de itens como completos/incompletos

## Planejamento de Desenvolvimento

### **FASE 1: CONFIGURAÇÃO E ESTRUTURA BASE**

#### 1. Configuração inicial do ambiente de desenvolvimento
- 1.1. Criar estrutura de pastas do projeto
- 1.2. Inicializar repositório Git
- 1.3. Criar arquivos .gitignore para Python e Node.js
- 1.4. Configurar variáveis de ambiente (.env e .env.local)

#### 2. Implementar estrutura do backend com FastAPI
- 2.1. Criar ambiente virtual Python
- 2.2. Instalar dependências do backend
- 2.3. Criar estrutura básica de pastas (app/, alembic/)
- 2.4. Configurar arquivo main.py com FastAPI básico
- 2.5. Configurar CORS para comunicação com frontend

#### 3. Configurar banco de dados PostgreSQL e Alembic
- 3.1. Instalar e configurar PostgreSQL localmente
- 3.2. Criar database "checklist_db"
- 3.3. Configurar conexão com SQLAlchemy
- 3.4. Inicializar Alembic para migrações
- 3.5. Criar arquivo database.py com configurações

### **FASE 2: BACKEND - AUTENTICAÇÃO E MODELOS**

#### 4. Implementar autenticação OAuth Google no backend
- 4.1. Configurar credenciais no Google Cloud Console
- 4.2. Implementar módulo auth.py
- 4.3. Criar endpoints de autenticação
- 4.4. Implementar JWT tokens para sessão
- 4.5. Criar middleware de autenticação

#### 5. Criar models e schemas do backend
- 5.1. Definir modelo User (SQLAlchemy)
- 5.2. Definir modelo Checklist
- 5.3. Definir modelo ChecklistItem
- 5.4. Criar schemas Pydantic correspondentes
- 5.5. Executar primeira migração com Alembic

#### 6. Implementar endpoints da API REST
- 6.1. CRUD de checklists (GET, POST, PUT, DELETE)
- 6.2. CRUD de items do checklist
- 6.3. Endpoint para toggle de item completo/incompleto
- 6.4. Implementar paginação e filtros
- 6.5. Adicionar validações e tratamento de erros

### **FASE 3: FRONTEND - ESTRUTURA BASE**

#### 7. Configurar estrutura inicial do frontend Next.js
- 7.1. Criar aplicação Next.js
- 7.2. Configurar estrutura de pastas
- 7.3. Configurar next.config.js
- 7.4. Criar layout base
- 7.5. Configurar rotas básicas

#### 8. Instalar e configurar Shadcn/UI e Tailwind CSS
- 8.1. Instalar Tailwind CSS
- 8.2. Configurar tailwind.config.js
- 8.3. Instalar componentes Shadcn/UI necessários
- 8.4. Configurar tema e cores
- 8.5. Criar arquivo globals.css

### **FASE 4: FRONTEND - AUTENTICAÇÃO E PÁGINAS**

#### 9. Implementar autenticação OAuth Google no frontend
- 9.1. Configurar @react-oauth/google
- 9.2. Criar contexto de autenticação
- 9.3. Implementar hook useAuth
- 9.4. Criar serviço de API com axios
- 9.5. Implementar interceptors para tokens

#### 10. Criar página de login
- 10.1. Design da página de login
- 10.2. Implementar botão "Entrar com Google"
- 10.3. Adicionar loading states
- 10.4. Implementar redirecionamento pós-login
- 10.5. Tratar erros de autenticação

#### 11. Desenvolver dashboard com listagem de checklists
- 11.1. Criar layout do dashboard
- 11.2. Implementar grid/lista de checklists
- 11.3. Criar componente ChecklistCard
- 11.4. Adicionar indicadores de progresso
- 11.5. Implementar estado vazio (sem checklists)

#### 12. Implementar formulário de criação de checklist
- 12.1. Criar modal/página de criação
- 12.2. Implementar formulário dinâmico
- 12.3. Adicionar/remover itens dinamicamente
- 12.4. Validação de formulário
- 12.5. Integração com API

### **FASE 5: FUNCIONALIDADES E INTEGRAÇÃO**

#### 13. Criar componentes de UI reutilizáveis
- 13.1. Button, Input, Card components
- 13.2. Modal/Dialog component
- 13.3. Loading e Error states
- 13.4. Toast notifications
- 13.5. Componente de confirmação

#### 14. Implementar funcionalidades CRUD de checklists
- 14.1. Visualizar detalhes do checklist
- 14.2. Editar checklist existente
- 14.3. Deletar checklist com confirmação
- 14.4. Duplicar checklist
- 14.5. Ordenação e filtros

#### 15. Adicionar gerenciamento de itens do checklist
- 15.1. Marcar/desmarcar itens
- 15.2. Adicionar novos itens
- 15.3. Editar itens existentes
- 15.4. Remover itens
- 15.5. Reordenar itens (drag and drop)

#### 16. Implementar integração frontend-backend
- 16.1. Configurar chamadas de API
- 16.2. Implementar loading states
- 16.3. Cache e otimização
- 16.4. Tratamento de erros global
- 16.5. Sincronização de dados

### **FASE 6: FINALIZAÇÃO**

#### 17. Testes e ajustes finais
- 17.1. Testes de integração
- 17.2. Ajustes de UI/UX
- 17.3. Otimização de performance
- 17.4. Correção de bugs
- 17.5. Documentação de uso

#### 18. Configurar Docker e docker-compose
- 18.1. Criar Dockerfile para backend
- 18.2. Criar Dockerfile para frontend
- 18.3. Configurar docker-compose.yml
- 18.4. Adicionar container PostgreSQL
- 18.5. Testar deploy containerizado

## Estrutura de Pastas do Projeto

```
checklist/
├── frontend/
│   ├── app/
│   │   ├── layout.js
│   │   ├── page.js
│   │   ├── dashboard/
│   │   │   └── page.js
│   │   └── api/
│   │       └── auth/
│   ├── components/
│   │   ├── ui/
│   │   ├── ChecklistCard.js
│   │   ├── ChecklistForm.js
│   │   └── GoogleLoginButton.js
│   ├── lib/
│   │   └── utils.js
│   ├── styles/
│   │   └── globals.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── next.config.js
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── auth.py
│   ├── alembic/
│   │   ├── alembic.ini
│   │   └── versions/
│   ├── requirements.txt
│   └── .env
│
├── docker-compose.yml
├── README.md
└── CLAUDE.md
```

## Comandos Úteis

### Backend
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor de desenvolvimento
uvicorn app.main:app --reload

# Criar nova migração
alembic revision --autogenerate -m "Descrição da migração"

# Aplicar migrações
alembic upgrade head
```

### Frontend
```bash
# Instalar dependências
npm install

# Rodar servidor de desenvolvimento
npm run dev

# Build de produção
npm run build

# Rodar build de produção
npm start
```

### Docker
```bash
# Subir todos os containers
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down
```

## Variáveis de Ambiente

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/checklist_db
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
SECRET_KEY=sua_chave_secreta_aqui
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_GOOGLE_CLIENT_ID=seu_client_id_aqui
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Status do Desenvolvimento

- [ ] Fase 1: Configuração e Estrutura Base
- [ ] Fase 2: Backend - Autenticação e Modelos
- [ ] Fase 3: Frontend - Estrutura Base
- [ ] Fase 4: Frontend - Autenticação e Páginas
- [ ] Fase 5: Funcionalidades e Integração
- [ ] Fase 6: Finalização

**Última atualização**: 28/07/2025