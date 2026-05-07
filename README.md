## Telhado Verde - Backend

API de monitoramento desenvolvida com **FastAPI**.

### Pré-requisitos
* Python 3.13+
* Poetry
* Docker & Docker Compose

### Instalação e Configuração

1. **Dependências:**
   ```bash
   poetry install
   ```

2. **Ambiente:**
   Crie um arquivo `.env`:
   ```env
   DATABASE_URL=mysql+pymysql://root:root@localhost:3306/telhado_verde
   ```

3. **Banco de Dados:**
   ```bash
   docker compose up -d
   poetry run alembic upgrade head
   ```

### Scripts e Execução

* **Popular dados (Opcional):**
  
```bash
  poetry run python seed.py
  ```

* **Iniciar Servidor:**
  ```bash
  poetry run uvicorn app.main:app --reload
  ```

Acesse em: `http://localhost:8000`
```