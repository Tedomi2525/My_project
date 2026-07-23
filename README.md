# He thong thi trac nghiem truc tuyen

Du an xay dung he thong quan ly va thi trac nghiem truc tuyen cho ba nhom nguoi dung: Admin, Giang vien va Sinh vien.

## Tong quan

- `frontend/`: ung dung Nuxt 4, Vue 3, TypeScript, Tailwind CSS 4.
- `backend/`: ung dung FastAPI monolith, SQLAlchemy va MySQL, chay tai cong `8000`.
- `docs/`: tai lieu, UML, ERD, DFD va anh giao dien cua do an.

## Chuc nang chinh

- Dang nhap bang JWT va phan quyen theo vai tro `admin`, `teacher`, `student`.
- Admin quan ly giao vien, sinh vien va duyet yeu cau tai khoan.
- Giang vien quan ly lop hoc, ngan hang cau hoi, import cau hoi CSV, tao de thi, tron cau hoi/dap an va xem thong ke ket qua.
- Sinh vien xem cac bai thi duoc phep, lam bai, ghi nhan vi pham trong qua trinh thi va xem lich su/phan tich ket qua.
- Gui email thong bao tai khoan moi neu cau hinh SMTP.

## Cong nghe su dung

**Frontend**

- Nuxt 4, Vue 3, Vue Router, TypeScript
- Tailwind CSS 4
- Axios, jwt-decode
- Chart.js, vue-chartjs
- lucide-vue-next, radix-vue

**Backend**

- FastAPI, Uvicorn
- SQLAlchemy, PyMySQL
- Pydantic, email-validator
- python-jose, passlib, bcrypt
- python-dotenv

**Database**

- MySQL 8+

## Cau truc thu muc

```text
My_project/
|-- backend/
|   |-- app/                    # Source chinh cua FastAPI monolith va shared code
|   |   |-- routers/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- core/
|   |   |-- main.py
|   |-- scripts/                # Script migrate/seed/cleanup du lieu
|   |-- create_first_admin.py
|   `-- requirements.txt
|-- frontend/
|   |-- app/
|   |   |-- pages/
|   |   |-- layouts/
|   |   |-- components/
|   |   |-- composables/
|   |   |-- services/
|   |   `-- types/
|   |-- nuxt.config.ts
|   `-- package.json
|-- docs/
|-- requirements.txt
|-- package.json
`-- README.md
```

## Yeu cau moi truong

- Python 3.10+
- Node.js 20+
- npm 10+
- MySQL 8+

## Cau hinh backend

Tao file cau hinh rieng trong `backend/.env` dua tren `backend/.env.example`, sau do dien thong tin database, JWT secret, CORS va SMTP phu hop voi may dang chay.

Khong commit file `.env` len Git. Project da co rule ignore cho cac file env cuc bo. Neu khong cau hinh SMTP, he thong van chay binh thuong nhung email thong bao tai khoan se khong duoc gui.

## Cai dat backend

```bash
cd backend
python -m venv venv
```

Kich hoat virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Cai thu vien Python:

```bash
pip install -r requirements.txt
```

Tao database MySQL truoc khi chay app:

```sql
CREATE DATABASE exam_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Chay backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Frontend mac dinh ket noi den backend tai `http://127.0.0.1:8000`. Co the thay doi dia chi bang bien moi truong `NUXT_PUBLIC_API_BASE`.

## Khoi tao tai khoan admin

Sau khi backend ket noi duoc database:

```bash
cd backend
python create_first_admin.py
```

Tai khoan mac dinh duoc tao:

- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com`

Nen doi mat khau/secret khi dua len moi truong that.

## Cai dat va chay frontend

```bash
cd frontend
npm install
npm run dev
```

Mo trinh duyet tai:

```text
http://localhost:3000
```

Tuy chinh API base cho frontend bang file env cuc bo trong `frontend/` neu can.

## Script frontend

- `npm run dev`: chay moi truong phat trien.
- `npm run build`: build production.
- `npm run preview`: xem ban build production.
- `npm run generate`: generate static site.

## Cac nhom API chinh

- `POST /login`
- `/admins`
- `/teachers`
- `/students`
- `/account-requests`
- `/classes`
- `/questions`
- `/exams`
- `/results`

## Ghi chu

- Database schema duoc tao tu SQLAlchemy models khi backend khoi dong.
- Cac script trong `backend/scripts/` ho tro seed demo, migrate chu de cau hoi, dong bo user cu va don trung lap de thi.
- File `requirements.txt` o thu muc goc va `backend/requirements.txt` dung cho phan backend Python; dependency frontend nam trong `frontend/package.json`.
