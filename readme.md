Write(README.md)
  ⎿  User rejected write to README.md
         1 +  # Checklist App
         2 +  
         3 +  ## Descrição
         4 +  Aplicativo web para criação e gerenciamento de checklists para diversos tipos de 
           + processos. O sistema permite que usuários criem, editem e acompanhem suas listas de 
     tarefas
           +  de forma organizada e intuitiva.
         5 +  
         6 +  ## Tecnologias Utilizadas
         7 +  
         8 +  ### Frontend
         9 +  - **Next.js** - Framework React para aplicações web
        10 +  - **React** - Biblioteca JavaScript para construção de interfaces
        11 +  - **Shadcn/UI** - Componentes de interface reutilizáveis
        12 +  - **Tailwind CSS** - Framework CSS utilitário para estilização
        13 +  
        14 +  ### Backend
        15 +  - **FastAPI** - Framework Python moderno para construção de APIs
        16 +  - **PostgreSQL** - Banco de dados relacional
        17 +  - **Alembic** - Ferramenta de migração de banco de dados para SQLAlchemy
        18 +  - **SQLAlchemy** - ORM Python para interação com o banco de dados
        19 +  
        20 +  ### Autenticação
        21 +  - **OAuth 2.0 Google** - Autenticação via conta Google
        22 +  
        23 +  ## Bibliotecas e Dependências
        24 +  
        25 +  ### Frontend (package.json)
        26 +  ```json
        27 +  {
        28 +    "dependencies": {
        29 +      "next": "latest",
        30 +      "react": "latest",
        31 +      "react-dom": "latest",
        32 +      "@radix-ui/react-alert-dialog": "latest",
        33 +      "@radix-ui/react-aspect-ratio": "latest",
        34 +      "@radix-ui/react-avatar": "latest",
        35 +      "@radix-ui/react-checkbox": "latest",
        36 +      "@radix-ui/react-dialog": "latest",
        37 +      "@radix-ui/react-dropdown-menu": "latest",
        38 +      "@radix-ui/react-label": "latest",
        39 +      "@radix-ui/react-select": "latest",
        40 +      "@radix-ui/react-separator": "latest",
        41 +      "@radix-ui/react-slot": "latest",
        42 +      "@radix-ui/react-switch": "latest",
        43 +      "@radix-ui/react-tabs": "latest",
        44 +      "@radix-ui/react-toast": "latest",
        45 +      "class-variance-authority": "latest",
        46 +      "clsx": "latest",
        47 +      "lucide-react": "latest",
        48 +      "tailwind-merge": "latest",
        49 +      "tailwindcss-animate": "latest",
        50 +      "@react-oauth/google": "latest",
        51 +      "axios": "latest"
        52 +    },
        53 +    "devDependencies": {
        54 +      "tailwindcss": "latest",
        55 +      "postcss": "latest",
        56 +      "autoprefixer": "latest"
        57 +    }
        58 +  }
        59 +  ```
        60 +  
        61 +  ### Backend (requirements.txt)
        62 +  ```
        63 +  fastapi==0.104.1
        64 +  uvicorn==0.24.0
        65 +  sqlalchemy==2.0.23
        66 +  alembic==1.12.1
        67 +  psycopg2-binary==2.9.9
        68 +  python-jose[cryptography]==3.3.0
        69 +  passlib[bcrypt]==1.7.4
        70 +  python-multipart==0.0.6
        71 +  python-dotenv==1.0.0
        72 +  httpx==0.25.1
        73 +  google-auth==2.23.4
        74 +  google-auth-oauthlib==1.1.0
        75 +  google-auth-httplib2==0.1.1
        76 +  pydantic==2.5.0
        77 +  pydantic-settings==2.1.0
        78 +  ```
        79 +  
        80 +  ## Jornada do Usuário
        81 +  
        82 +  ### 1. Login
        83 +  - O usuário acessa a página inicial do aplicativo
        84 +  - Clica no botão "Entrar com Google"
        85 +  - É redirecionado para a página de autenticação do Google
        86 +  - Após autenticar, é redirecionado de volta ao aplicativo
        87 +  
        88 +  ### 2. Dashboard
        89 +  - Após o login, o usuário é direcionado ao dashboard
        90 +  - No dashboard, visualiza todos os seus checklists criados
        91 +  - Cada checklist exibe:
        92 +    - Título
        93 +    - Data de criação
        94 +    - Progresso (itens concluídos/total)
        95 +    - Ações (visualizar, editar, excluir)
        96 +  
        97 +  ### 3. Criação de Checklist
        98 +  - Se não houver checklists, é exibida uma mensagem amigável
        99 +  - O usuário clica no botão "Criar Checklist"
       100 +  - Um formulário é apresentado com os campos:
       101 +    - Título do checklist
       102 +    - Descrição (opcional)
       103 +    - Itens do checklist (campo dinâmico para adicionar múltiplos itens)
       104 +  
       105 +  ### 4. Formulário de Criação
       106 +  - O usuário preenche o título do checklist
       107 +  - Adiciona itens ao checklist usando o botão "Adicionar Item"
       108 +  - Cada item pode ter:
       109 +    - Descrição
       110 +    - Prioridade (opcional)
       111 +    - Prazo (opcional)
       112 +  - Pode reordenar os itens arrastando
       113 +  - Pode remover itens individualmente
       114 +  
       115 +  ### 5. Salvamento
       116 +  - Após preencher todos os campos desejados, clica em "OK" ou "Criar Checklist"
       117 +  - O sistema valida os dados
       118 +  - Se válido, o checklist é criado e salvo no banco de dados
       119 +  - O usuário é redirecionado ao dashboard onde pode ver o novo checklist
       120 +  
       121 +  ## Estrutura do Projeto
       122 +  
       123 +  ```
       124 +  checklist/
       125 +  ├── frontend/
       126 +  │   ├── app/
       127 +  │   │   ├── layout.js
       128 +  │   │   ├── page.js
       129 +  │   │   ├── dashboard/
       130 +  │   │   │   └── page.js
       131 +  │   │   └── api/
       132 +  │   │       └── auth/
       133 +  │   ├── components/
       134 +  │   │   ├── ui/
       135 +  │   │   ├── ChecklistCard.js
       136 +  │   │   ├── ChecklistForm.js
       137 +  │   │   └── GoogleLoginButton.js
       138 +  │   ├── lib/
       139 +  │   │   └── utils.js
       140 +  │   ├── styles/
       141 +  │   │   └── globals.css
       142 +  │   ├── package.json
       143 +  │   ├── tailwind.config.js
       144 +  │   └── next.config.js
       145 +  │
       146 +  ├── backend/
       147 +  │   ├── app/
       148 +  │   │   ├── __init__.py
       149 +  │   │   ├── main.py
       150 +  │   │   ├── database.py
       151 +  │   │   ├── models.py
       152 +  │   │   ├── schemas.py
       153 +  │   │   ├── crud.py
       154 +  │   │   └── auth.py
       155 +  │   ├── alembic/
       156 +  │   │   ├── alembic.ini
       157 +  │   │   └── versions/
       158 +  │   ├── requirements.txt
       159 +  │   └── .env
       160 +  │
       161 +  ├── docker-compose.yml
       162 +  └── README.md
       163 +  ```
       164 +  
       165 +  ## Instalação e Configuração
       166 +  
       167 +  ### Pré-requisitos
       168 +  - Node.js (v18+)
       169 +  - Python 3.9+
       170 +  - PostgreSQL
       171 +  - Conta no Google Cloud Console para OAuth
       172 +  
       173 +  ### Configuração do Google OAuth
       174 +  1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
       175 +  2. Crie um novo projeto ou selecione um existente
       176 +  3. Ative a API do Google+ 
       177 +  4. Configure as credenciais OAuth 2.0
       178 +  5. Adicione as URLs de redirecionamento autorizadas
       179 +  6. Copie o Client ID e Client Secret
       180 +  
       181 +  ### Variáveis de Ambiente
       182 +  
       183 +  #### Backend (.env)
       184 +  ```
       185 +  DATABASE_URL=postgresql://user:password@localhost:5432/checklist_db
       186 +  GOOGLE_CLIENT_ID=seu_client_id_aqui
       187 +  GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
       188 +  SECRET_KEY=sua_chave_secreta_aqui
       189 +  FRONTEND_URL=http://localhost:3000
       190 +  ```
       191 +  
       192 +  #### Frontend (.env.local)
       193 +  ```
       194 +  NEXT_PUBLIC_GOOGLE_CLIENT_ID=seu_client_id_aqui
       195 +  NEXT_PUBLIC_API_URL=http://localhost:8000
       196 +  ```
       197 +  
       198 +  ## Rodando o Projeto
       199 +  
       200 +  ### Backend
       201 +  ```bash
       202 +  cd backend
       203 +  pip install -r requirements.txt
       204 +  alembic init alembic
       205 +  alembic revision --autogenerate -m "Initial migration"
       206 +  alembic upgrade head
       207 +  uvicorn app.main:app --reload
       208 +  ```
       209 +  
       210 +  ### Frontend
       211 +  ```bash
       212 +  cd frontend
       213 +  npm install
       214 +  npm run dev
       215 +  ```
       216 +  
       217 +  ### Docker (opcional)
       218 +  ```bash
       219 +  docker-compose up -d
       220 +  ```
       221 +  
       222 +  ## API Endpoints
       223 +  
       224 +  ### Autenticação
       225 +  - `POST /auth/google` - Login com Google
       226 +  - `GET /auth/me` - Obter usuário atual
       227 +  - `POST /auth/logout` - Logout
       228 +  
       229 +  ### Checklists
       230 +  - `GET /checklists` - Listar todos os checklists do usuário
       231 +  - `POST /checklists` - Criar novo checklist
       232 +  - `GET /checklists/{id}` - Obter checklist específico
       233 +  - `PUT /checklists/{id}` - Atualizar checklist
       234 +  - `DELETE /checklists/{id}` - Excluir checklist
       235 +  
       236 +  ### Itens do Checklist
       237 +  - `POST /checklists/{id}/items` - Adicionar item ao checklist
       238 +  - `PUT /checklists/{id}/items/{item_id}` - Atualizar item
       239 +  - `DELETE /checklists/{id}/items/{item_id}` - Remover item
       240 +  - `PATCH /checklists/{id}/items/{item_id}/toggle` - Marcar/desmarcar item
       241 +  
       242 +  ## Modelo de Dados
       243 +  
       244 +  ### User
       245 +  - id (UUID)
       246 +  - email (String)
       247 +  - name (String)
       248 +  - google_id (String)
       249 +  - created_at (DateTime)
       250 +  
       251 +  ### Checklist
       252 +  - id (UUID)
       253 +  - user_id (UUID, FK)
       254 +  - title (String)
       255 +  - description (String, opcional)
       256 +  - created_at (DateTime)
       257 +  - updated_at (DateTime)
       258 +  
       259 +  ### ChecklistItem
       260 +  - id (UUID)
       261 +  - checklist_id (UUID, FK)
       262 +  - description (String)
       263 +  - is_completed (Boolean)
       264 +  - priority (String, opcional)
       265 +  - due_date (DateTime, opcional)
       266 +  - order (Integer)
       267 +  - created_at (DateTime)
       268 +  - updated_at (DateTime)
       269   \ No newline at end of file