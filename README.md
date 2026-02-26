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
### 1) Backend (FastAPI)
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
pip install fastapi "uvicorn[standard]" sqlalchemy pymysql python-dotenv "passlib[bcrypt]" "python-jose[cryptography]" email-validator
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

## Auth hien tai (can luu y)
- Backend co endpoint `POST /login` tra ve `access_token`
- Nhieu endpoint nghiep vu dang xac thuc qua header `x-user-id`
- Frontend hien tai dang gui `x-user-id` cho mot so API (de phu hop voi backend hien co)

Neu ban phat trien tiep auth JWT full flow, nen dong bo lai:
- backend dependencies (`get_current_user`) theo Bearer token
- frontend headers `Authorization: Bearer <token>`

## Endpoint nhom chinh
- Auth: `/login`
- Users: `/users`
- Classes: `/classes`
- Questions: `/questions`
- Exams: `/exams`
- Results: `/results`

## Ghi chu
- `backend/requirements.txt` hien dang trong. Nen cap nhat file nay de team cai dat dong nhat:
```bash
pip freeze > requirements.txt
```
- Khong commit file `.env` len git.

## Huong phat trien tiep (goi y)
- Hoan thien luong JWT xac thuc thong nhat
- Bo sung migration (Alembic)
- Them test backend/frontend
- Them Docker Compose cho toan bo he thong
