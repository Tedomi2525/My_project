# He thong Thi Trac Nghiem (Quiz App)

Du an gom 2 phan:
- `frontend/`: Nuxt 4 + Vue 3 + TailwindCSS (giao dien cho Admin, Teacher, Student)
- `backend/`: FastAPI + SQLAlchemy + MySQL (REST API cho quan ly de thi, lop hoc, ket qua)

## Tinh nang chinh
- Dang nhap va phan quyen theo vai tro: `admin`, `teacher`, `student`
- Admin: quan ly nguoi dung
- Teacher: quan ly lop hoc, cau hoi, de thi, thong ke ket qua
- Student: xem bai thi duoc phep, lam bai, xem lich su

## Cong nghe su dung
- Frontend: Nuxt 4, Vue 3, TypeScript, TailwindCSS 4, Chart.js
- Backend: FastAPI, SQLAlchemy, Pydantic, Passlib, python-jose
- Database: MySQL

## Cau truc thu muc
```text
My_project/
|-- frontend/
|   |-- app/
|   |-- nuxt.config.ts
|   `-- package.json
|-- backend/
|   |-- app/
|   |-- create_first_admin.py
|   |-- requirements.txt
|   `-- .env
|-- package.json
`-- README.md
```

## Yeu cau moi truong
- Node.js >= 20
- npm >= 10
- Python >= 3.10
- MySQL >= 8

## Cai dat va chay du an
### 1) Backend (FastAPI monolith)
Di vao thu muc backend:
```bash
cd backend
```

Tao virtual environment (neu chua co):
```bash
python -m venv venv
```

Kich hoat venv:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Cai dependency:
```bash
pip install -r requirements.txt
```

Tao file `.env` trong `backend/` (neu chua co):
```env
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=exam_system
```

Chay API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 1b) Backend microservices
Kien truc microservices hien tai tach vat ly thanh nhieu FastAPI process, nhung van dung chung database MySQL hien tai de giam rui ro khi chuyen doi.

```text
Frontend Nuxt/Vue
      |
      v
API Gateway :8100
      |
      |-- Auth Service      :8101
      |-- User Service      :8102
      |-- Class Service     :8103
      |-- Question Service  :8104
      |-- Exam Service      :8105
      `-- Result Service    :8106
```

Cai them dependency neu chua co:
```bash
cd backend
pip install -r requirements.txt
```

Chay tat ca service tren Windows PowerShell:
```powershell
cd backend
.\run_microservices.ps1
```

Dung tat ca service:
```powershell
cd backend
.\stop_microservices.ps1
```

Log cua tung service nam trong `backend/logs/`.

Hoac chay tung service:
```bash
uvicorn gateway.main:app --reload --host 127.0.0.1 --port 8100
uvicorn services.auth_service.main:app --reload --host 127.0.0.1 --port 8101
uvicorn services.user_service.main:app --reload --host 127.0.0.1 --port 8102
uvicorn services.class_service.main:app --reload --host 127.0.0.1 --port 8103
uvicorn services.question_service.main:app --reload --host 127.0.0.1 --port 8104
uvicorn services.exam_service.main:app --reload --host 127.0.0.1 --port 8105
uvicorn services.result_service.main:app --reload --host 127.0.0.1 --port 8106
```

Frontend dung base URL `http://127.0.0.1:8100`; gateway se tu chuyen tiep request den service phu hop.

Cau truc backend microservices:
```text
backend/
|-- gateway/
|   |-- __init__.py
|   `-- main.py
|-- services/
|   |-- auth_service/
|   |   |-- main.py
|   |   |-- routers/
|   |   |-- schemas/
|   |   `-- services/
|   |-- user_service/
|   |   |-- main.py
|   |   |-- routers/
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   |-- class_service/
|   |   |-- main.py
|   |   |-- routers/
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   |-- question_service/
|   |   |-- main.py
|   |   |-- routers/
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   |-- exam_service/
|   |   |-- main.py
|   |   |-- routers/
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   `-- result_service/
|       |-- main.py
|       |-- routers/
|       |-- models/
|       |-- schemas/
|       `-- services/
`-- app/
    `-- shared code hien tai: database, models, routers, schemas, services
```

Khoi tao tai khoan admin dau tien:
```bash
python create_first_admin.py
```
Tai khoan mac dinh do script tao:
- Username: `admin`
- Password: `admin123`

### 2) Frontend (Nuxt)
Di vao thu muc frontend:
```bash
cd frontend
```

Cai dependency:
```bash
npm install
```

Chay moi truong dev:
```bash
npm run dev
```

Mo trinh duyet: `http://localhost:3000`

## Script hay dung
Trong `frontend/package.json`:
- `npm run dev`: chay dev
- `npm run build`: build production
- `npm run preview`: chay ban build
- `npm run generate`: generate static

## Endpoint nhom chinh
- Auth: `/login`
- Users: `/users`
- Classes: `/classes`
- Questions: `/questions`
- Exams: `/exams`
- Results: `/results`


