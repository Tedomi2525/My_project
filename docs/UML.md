# Tài liệu UML đầy đủ - Hệ thống Thi Trắc Nghiệm

## 0) Phạm vi tài liệu
Tài liệu này mô tả đầy đủ các chức năng theo **backend hiện tại** (FastAPI), gồm các nhóm API:
- `/login`
- `/users`
- `/classes`
- `/questions`
- `/exams`
- `/results`
- `/` (health check)

Lưu ý triển khai hiện tại:
- Đăng nhập trả JWT ở `/login`.
- Nhiều API nghiệp vụ đang xác thực bằng header `x-user-id`.

## 1) Danh sách đầy đủ các use-case

### Nhóm A - Xác thực

#### UC-A1: Đăng nhập hệ thống
- Tác nhân: Admin/Teacher/Student
- API: `POST /login`
- Tiền điều kiện: Có tài khoản hợp lệ
- Kết quả: Nhận `access_token`, `user_id`, `role`, `full_name`

#### UC-A2: Kiểm tra trạng thái API
- Tác nhân: Bất kỳ client
- API: `GET /`
- Kết quả: Nhận thông báo API đang chạy

### Nhóm B - Quản lý người dùng (`/users`)

#### UC-B1: Tạo người dùng
- Tác nhân: Quản trị vận hành (theo nghiệp vụ)
- API: `POST /users`
- Kết quả: Tạo user mới (student/teacher/admin)

#### UC-B2: Xem danh sách người dùng
- API: `GET /users`
- Kết quả: Trả danh sách user (có phân trang `skip`, `limit`)

#### UC-B3: Xem chi tiết người dùng
- API: `GET /users/{user_id}`

#### UC-B4: Cập nhật người dùng
- API: `PUT /users/{user_id}`
- Kết quả: Cập nhật thông tin user, có thể đổi mật khẩu

#### UC-B5: Xóa người dùng
- API: `DELETE /users/{user_id}`

### Nhóm C - Quản lý lớp học (`/classes`)

#### UC-C1: Giáo viên xem danh sách lớp của mình
- API: `GET /classes`

#### UC-C2: Giáo viên tạo lớp
- API: `POST /classes`

#### UC-C3: Giáo viên xem chi tiết lớp
- API: `GET /classes/{class_id}`

#### UC-C4: Giáo viên cập nhật lớp
- API: `PUT /classes/{class_id}`

#### UC-C5: Giáo viên xóa lớp
- API: `DELETE /classes/{class_id}`

#### UC-C6: Giáo viên xem học sinh chưa thuộc lớp
- API: `GET /classes/{class_id}/available-students`

#### UC-C7: Giáo viên thêm học sinh vào lớp
- API: `POST /classes/{class_id}/students/{student_id}`

#### UC-C8: Giáo viên xóa học sinh khỏi lớp
- API: `DELETE /classes/{class_id}/students/{student_id}`

### Nhóm D - Quản lý câu hỏi (`/questions`)

#### UC-D1: Tạo câu hỏi
- API: `POST /questions`

#### UC-D2: Xem danh sách câu hỏi
- API: `GET /questions`

#### UC-D3: Xem chi tiết câu hỏi
- API: `GET /questions/{question_id}`

#### UC-D4: Cập nhật câu hỏi
- API: `PUT /questions/{question_id}`

#### UC-D5: Xóa câu hỏi
- API: `DELETE /questions/{question_id}`

### Nhóm E - Quản lý đề thi (`/exams`)

#### UC-E1: Giáo viên xem đề thi của mình
- API: `GET /exams`

#### UC-E2: Giáo viên tạo đề thi
- API: `POST /exams`
- Bao gồm: thông tin đề, danh sách lớp được phép (`class_ids`), danh sách câu hỏi (`questions`)

#### UC-E3: Học sinh xem các đề của mình
- API: `GET /exams/my-exams`

#### UC-E4: Xem chi tiết đề thi
- API: `GET /exams/{exam_id}`
- Có kiểm tra quyền truy cập đề

#### UC-E5: Cập nhật đề thi
- API: `PUT /exams/{exam_id}`
- Có kiểm tra quyền và cập nhật lớp/câu hỏi

#### UC-E6: Xóa đề thi
- API: `DELETE /exams/{exam_id}`

#### UC-E7: Xem danh sách câu hỏi trong đề
- API: `GET /exams/{exam_id}/questions`

#### UC-E8: Kiểm tra mật khẩu đề thi
- API: `POST /exams/{exam_id}/check-password`

### Nhóm F - Kết quả thi (`/results`)

#### UC-F1: Học sinh nộp bài thi
- API: `POST /results/submit/{exam_id}`
- Hệ thống chấm tự động, lưu `exam_result` và `exam_result_detail`

#### UC-F2: Xem một kết quả thi
- API: `GET /results/{result_id}`

#### UC-F3: Xem lịch sử thi của học sinh
- API: `GET /results/student/{student_id}`

#### UC-F4: Giáo viên xem kết quả theo đề
- API: `GET /results/exam/{exam_id}`

#### UC-F5: Review bài làm
- API: `GET /results/{result_id}/review`
- Student chỉ xem bài của mình và khi đề cho phép `allow_view_answers`
- Teacher chỉ xem bài thuộc đề do mình tạo

#### UC-F6: Cập nhật điểm thủ công
- API: `PUT /results/{result_id}/score`

#### UC-F7: Xóa kết quả thi
- API: `DELETE /results/{result_id}`

## 2) Mô hình Use-case tổng quan

```mermaid
flowchart LR
  Admin[Admin]
  Teacher[Teacher]
  Student[Student]
  Client[Client/Monitoring]

  subgraph System[Quiz Exam System]
    U1([Đăng nhập])
    U2([Kiểm tra trạng thái hệ thống])
    U3([Quản lý người dùng])
    U4([Quản lý lớp học])
    U5([Quản lý học sinh trong lớp])
    U6([Quản lý câu hỏi])
    U7([Quản lý đề thi])
    U8([Kiểm tra mật khẩu đề])
    U9([Xem đề được phép thi])
    U10([Nộp bài va chấm điểm])
    U11([Xem lịch sử/kết quả])
    U12([Review bài làm])
    U13([Sửa điểm/Xóa kết quả])
  end

  Admin --> U1
  Admin --> U3

  Teacher --> U1
  Teacher --> U4
  Teacher --> U5
  Teacher --> U6
  Teacher --> U7
  Teacher --> U8
  Teacher --> U11
  Teacher --> U12
  Teacher --> U13

  Student --> U1
  Student --> U8
  Student --> U9
  Student --> U10
  Student --> U11
  Student --> U12

  Client --> U2
```

## 3) Mô hình Use-case chi tiết theo phân hệ

```mermaid
flowchart LR
  Teacher[Teacher]
  Student[Student]

  subgraph ExamModule[Exam Module]
    E1([Tạo đề])
    E2([Sửa đề])
    E3([Xóa đề])
    E4([Xem đề])
    E5([Xem câu hỏi trong đề])
    E6([Kiểm tra mật khẩu đề])
    E7([Nộp bài])
    E8([Review kết quả])
  end

  Teacher --> E1
  Teacher --> E2
  Teacher --> E3
  Teacher --> E4
  Teacher --> E5
  Teacher --> E6
  Teacher --> E8

  Student --> E4
  Student --> E5
  Student --> E6
  Student --> E7
  Student --> E8
```

## 4) Biểu đồ luồng dữ liệu (DFD)

### 4.1 DFD mức ngữ cảnh (Context Diagram)

```mermaid
flowchart LR
  Admin[Admin]
  Teacher[Teacher]
  Student[Student]

  System((He thong thi trac nghiem))

  Admin -->|Thong tin tai khoan, yeu cau quan ly user| System
  System -->|Danh sach user, ket qua xu ly| Admin

  Teacher -->|Thong tin lop, cau hoi, de thi, yeu cau thong ke| System
  System -->|Danh sach lop, cau hoi, de thi, ket qua, thong ke| Teacher

  Student -->|Thong tin dang nhap, mat khau de, bai lam| System
  System -->|Danh sach de thi, cau hoi, ket qua, lich su thi| Student
```

### 4.2 DFD mức 0

```mermaid
flowchart TB
  Admin[Admin]
  Teacher[Teacher]
  Student[Student]

  P1((1. Quan ly xac thuc))
  P2((2. Quan ly nguoi dung))
  P3((3. Quan ly lop hoc))
  P4((4. Quan ly cau hoi))
  P5((5. Quan ly de thi))
  P6((6. Quan ly bai thi va ket qua))
  P7((7. Thong ke va review))

  D1[(D1. User)]
  D2[(D2. Class)]
  D3[(D3. Class_Student)]
  D4[(D4. Question)]
  D5[(D5. Exam)]
  D6[(D6. Exam_Question)]
  D7[(D7. Exam_Allowed_Class)]
  D8[(D8. Exam_Result)]
  D9[(D9. Exam_Result_Detail)]

  Admin -->|Thong tin dang nhap| P1
  Teacher -->|Thong tin dang nhap| P1
  Student -->|Thong tin dang nhap| P1
  P1 -->|Kiem tra tai khoan| D1
  P1 -->|Token, role, user_id| Admin
  P1 -->|Token, role, user_id| Teacher
  P1 -->|Token, role, user_id| Student

  Admin -->|Them/sua/xoa/xem user| P2
  P2 -->|Doc/ghi user| D1
  P2 -->|Danh sach user, thong bao| Admin

  Teacher -->|Tao/sua/xoa/xem lop, them/xoa SV| P3
  P3 -->|Doc/ghi lop hoc| D2
  P3 -->|Doc/ghi phan lop| D3
  P3 -->|Doc user sinh vien| D1
  P3 -->|Thong tin lop hoc| Teacher

  Teacher -->|Tao/sua/xoa/xem cau hoi| P4
  P4 -->|Doc/ghi cau hoi| D4
  P4 -->|Danh sach cau hoi| Teacher

  Teacher -->|Tao/sua/xoa/xem de thi| P5
  Student -->|Yeu cau xem de thi| P5
  Student -->|Nhap mat khau de| P5
  P5 -->|Doc/ghi de thi| D5
  P5 -->|Doc/ghi cau hoi trong de| D6
  P5 -->|Doc/ghi lop duoc phep thi| D7
  P5 -->|Thong tin de thi| Teacher
  P5 -->|Danh sach de, chi tiet de, ket qua kiem tra mat khau| Student

  Student -->|Bai lam, dap an| P6
  P6 -->|Doc de thi| D5
  P6 -->|Doc cau hoi de thi| D6
  P6 -->|Ghi ket qua thi| D8
  P6 -->|Ghi chi tiet bai lam| D9
  P6 -->|Ket qua thi, lich su thi| Student

  Teacher -->|Yeu cau thong ke, review bai lam| P7
  Student -->|Yeu cau xem review| P7
  P7 -->|Doc ket qua thi| D8
  P7 -->|Doc chi tiet bai lam| D9
  P7 -->|Doc cau hoi| D4
  P7 -->|Doc de thi| D5
  P7 -->|Bao cao, thong ke, review| Teacher
  P7 -->|Chi tiet bai lam| Student
```

### 4.3 DFD mức 1 cho phân hệ làm bài thi

```mermaid
flowchart LR
  Student[Student]

  P61((6.1 Lay de thi va cau hoi))
  P62((6.2 Lam bai va ghi nhan dap an))
  P63((6.3 Nop bai va cham diem))
  P64((6.4 Luu ket qua va lich su))

  D5[(Exam)]
  D6[(Exam_Question)]
  D4[(Question)]
  D8[(Exam_Result)]
  D9[(Exam_Result_Detail)]

  Student -->|Yeu cau vao thi| P61
  P61 -->|Doc thong tin de| D5
  P61 -->|Doc danh sach cau hoi| D6
  P61 -->|Doc noi dung cau hoi| D4
  P61 -->|De thi + cau hoi| Student

  Student -->|Lua chon dap an| P62
  P62 -->|Danh sach dap an tam thoi| P63

  Student -->|Yeu cau nop bai| P63
  P63 -->|Doc dap an dung| D4
  P63 -->|Tinh diem| P64

  P64 -->|Luu ket qua tong| D8
  P64 -->|Luu chi tiet tung cau| D9
  P64 -->|Ket qua thi| Student
```

### 4.4 DFD mức 1 cho phân hệ thống kê và review

```mermaid
flowchart LR
  Teacher[Teacher]
  Student[Student]

  P71((7.1 Lay ket qua theo de thi))
  P72((7.2 Tong hop thong ke))
  P73((7.3 Lay chi tiet review))
  P74((7.4 Tra bao cao va bai lam))

  D8[(Exam_Result)]
  D9[(Exam_Result_Detail)]
  D4[(Question)]
  D5[(Exam)]

  Teacher -->|Chon de thi can xem thong ke| P71
  P71 -->|Doc ket qua theo de| D8
  P71 -->|Danh sach ket qua| P72

  P72 -->|Doc chi tiet bai lam| D9
  P72 -->|Doc cau hoi| D4
  P72 -->|Thong ke diem, do kho| P74

  Teacher -->|Chon bai lam can review| P73
  Student -->|Yeu cau xem bai lam| P73
  P73 -->|Doc ket qua thi| D8
  P73 -->|Doc chi tiet bai lam| D9
  P73 -->|Doc cau hoi va thong tin de| D4
  P73 -->|Doc thong tin de thi| D5
  P73 -->|Du lieu review| P74

  P74 -->|Bao cao thong ke, chi tiet bai lam| Teacher
  P74 -->|Chi tiet bai lam| Student
```

## 5) Mô hình lớp (Class Diagram)

```mermaid
classDiagram
class User {
  +int id
  +string username
  +string email
  +string password
  +string full_name
  +string role
  +string student_code
}

class Class {
  +int id
  +string name
  +string description
  +int teacher_id
}

class ClassStudent {
  +int id
  +int class_id
  +int student_id
  +datetime joined_at
}

class Question {
  +int id
  +text content
  +string question_type
  +enum difficulty
  +json options
  +string correct_answer
  +int created_by
}

class Exam {
  +int id
  +string title
  +text description
  +int duration_minutes
  +datetime start_time
  +datetime end_time
  +string password
  +int created_by
  +bool allow_view_answers
  +int? max_attempts
  +bool shuffle_questions
  +bool shuffle_options
}

class ExamQuestion {
  +int id
  +int exam_id
  +int question_id
}

class ExamAllowedClass {
  +int id
  +int exam_id
  +int class_id
}

class ExamResult {
  +int id
  +int exam_id
  +int student_id
  +float total_score
  +datetime started_at
  +datetime finished_at
}

class ExamResultDetail {
  +int id
  +int result_id
  +int question_id
  +string student_answer
  +bool is_correct
}

User "1" <-- "0..*" Class : teacher
User "1" <-- "0..*" ClassStudent : student
Class "1" <-- "0..*" ClassStudent : class_
Exam "1" <-- "0..*" ExamQuestion : exam
Question "1" <-- "0..*" ExamQuestion : question
Exam "1" <-- "0..*" ExamAllowedClass : exam
Exam "1" <-- "0..*" ExamResult : exam
User "1" <-- "0..*" ExamResult : student
ExamResult "1" <-- "0..*" ExamResultDetail : result
Question "1" <-- "0..*" ExamResultDetail : question

Question ..> User : created_by (FK)
Exam ..> User : created_by (FK)
ExamAllowedClass ..> Class : class_id (FK)
```

### 5.1 Class Diagram theo hướng thiết kế có methods

Lưu ý: sơ đồ dưới đây là bản phục vụ báo cáo phân tích thiết kế hướng đối tượng, nên có bổ sung các thao tác nghiệp vụ chính. Nó không nhằm phản ánh 1:1 các method đang nằm trong file model Python.

```mermaid
classDiagram
class User {
  +int id
  +string username
  +string email
  +string password
  +string full_name
  +string role
  +string student_code
  +login()
  +logout()
  +updateProfile()
}

class Admin {
  +createUser()
  +updateUser()
  +deleteUser()
  +viewUsers()
}

class Teacher {
  +createClass()
  +updateClass()
  +deleteClass()
  +addStudentToClass()
  +removeStudentFromClass()
  +createQuestion()
  +updateQuestion()
  +deleteQuestion()
  +createExam()
  +updateExam()
  +deleteExam()
  +viewStatistics()
  +reviewResult()
}

class Student {
  +viewMyExams()
  +checkExamPassword()
  +startExam()
  +submitExam()
  +viewHistory()
  +reviewOwnResult()
}

class Class {
  +int id
  +string name
  +string description
  +int teacher_id
  +addStudent()
  +removeStudent()
  +getStudentList()
}

class ClassStudent {
  +int id
  +int class_id
  +int student_id
  +datetime joined_at
}

class Question {
  +int id
  +text content
  +string question_type
  +enum difficulty
  +json options
  +string correct_answer
  +int created_by
  +create()
  +update()
  +delete()
}

class Exam {
  +int id
  +string title
  +text description
  +int duration_minutes
  +datetime start_time
  +datetime end_time
  +string password
  +int created_by
  +bool allow_view_answers
  +int? max_attempts
  +bool shuffle_questions
  +bool shuffle_options
  +checkPassword()
  +getQuestions()
  +publish()
}

class ExamQuestion {
  +int id
  +int exam_id
  +int question_id
}

class ExamAllowedClass {
  +int id
  +int exam_id
  +int class_id
}

class ExamResult {
  +int id
  +int exam_id
  +int student_id
  +float total_score
  +datetime started_at
  +datetime finished_at
  +calculateScore()
  +saveResult()
  +getReview()
}

class ExamResultDetail {
  +int id
  +int result_id
  +int question_id
  +string student_answer
  +bool is_correct
}

User <|-- Admin
User <|-- Teacher
User <|-- Student

Teacher "1" --> "0..*" Class : manages
Student "1" --> "0..*" ClassStudent : joins
Class "1" --> "0..*" ClassStudent : contains
Teacher "1" --> "0..*" Question : creates
Teacher "1" --> "0..*" Exam : creates
Exam "1" --> "0..*" ExamQuestion : has
Question "1" --> "0..*" ExamQuestion : belongs_to
Exam "1" --> "0..*" ExamAllowedClass : allows
Class "1" --> "0..*" ExamAllowedClass : assigned
Student "1" --> "0..*" ExamResult : receives
Exam "1" --> "0..*" ExamResult : produces
ExamResult "1" --> "0..*" ExamResultDetail : contains
Question "1" --> "0..*" ExamResultDetail : references
```

## 6) Mô hình đối tượng (Object Snapshot)

- `admin_1:User {id=1, role="admin"}`
- `teacher_5:User {id=5, role="teacher"}`
- `student_12:User {id=12, role="student", student_code="SE1201"}`
- `class_3:Class {id=3, name="SE401", teacher_id=5}`
- `class_student_1:ClassStudent {class_id=3, student_id=12}`
- `question_101:Question {id=101, difficulty="MEDIUM"}`
- `exam_10:Exam {id=10, created_by=5, max_attempts=1, allow_view_answers=true}`
- `exam_question_1:ExamQuestion {exam_id=10, question_id=101}`
- `allow_class_1:ExamAllowedClass {exam_id=10, class_id=3}`
- `result_55:ExamResult {exam_id=10, student_id=12, total_score=8.0}`
- `result_detail_1:ExamResultDetail {result_id=55, question_id=101, is_correct=true}`

## 7) Các biểu đồ tuần tự theo giao diện hiện tại

Lưu ý: phần này chỉ giữ các luồng đang có màn hình ở frontend hiện tại. Các API backend chưa có màn hình riêng như `sửa điểm` hoặc `xóa kết quả` không đưa vào đây.

### SD-01: Đăng nhập và điều hướng theo vai trò
```mermaid
sequenceDiagram
actor User
participant LoginPage as Login Page
participant AuthComposable as useAuth.login()
participant AuthAPI as POST /login
participant UserService
participant DB

User->>LoginPage: Nhập username/password
LoginPage->>AuthComposable: handleSubmit()
AuthComposable->>AuthAPI: Gửi thông tin đăng nhập
AuthAPI->>UserService: get_user_by_username()
UserService->>DB: SELECT user
DB-->>UserService: user
UserService-->>AuthAPI: verify_password()
AuthAPI-->>AuthComposable: access_token + user_id + role
AuthComposable-->>LoginPage: Lưu user/token
LoginPage-->>User: Điều hướng /admin, /teacher hoặc /student
```

### SD-02: Admin quản lý tài khoản người dùng
```mermaid
sequenceDiagram
actor Admin
participant AdminPage as admin/index.vue
participant UserAPI as /users
participant UserService
participant DB

Admin->>AdminPage: Mở trang quản lý user
AdminPage->>UserAPI: GET /users
UserAPI->>UserService: get_users()
UserService->>DB: SELECT users
DB-->>UserService: user list
UserService-->>UserAPI: users
UserAPI-->>AdminPage: danh sách tài khoản

alt Thêm tài khoản
  Admin->>AdminPage: Nhập form tạo mới
  AdminPage->>UserAPI: POST /users
  UserAPI->>UserService: create_user()
  UserService->>DB: INSERT user
  DB-->>UserService: created user
  UserAPI-->>AdminPage: UserResponse
else Sửa tài khoản
  Admin->>AdminPage: Cập nhật thông tin
  AdminPage->>UserAPI: PUT /users/{id}
  UserAPI->>UserService: update_user()
  UserService->>DB: UPDATE user
  DB-->>UserService: updated user
  UserAPI-->>AdminPage: UserResponse
else Xóa tài khoản
  Admin->>AdminPage: Xác nhận xóa
  AdminPage->>UserAPI: DELETE /users/{id}
  UserAPI->>UserService: delete_user()
  UserService->>DB: DELETE user
  UserAPI-->>AdminPage: success
end

AdminPage->>UserAPI: GET /users
UserAPI-->>AdminPage: danh sách mới
```

### SD-03: Teacher quản lý lớp học và sinh viên trong lớp
```mermaid
sequenceDiagram
actor Teacher
participant TeacherClassPage as teacher/index.vue
participant ClassAPI as /classes
participant Dep as get_current_user
participant ClassService
participant DB

Teacher->>TeacherClassPage: Mở trang lớp học
TeacherClassPage->>ClassAPI: GET /classes
ClassAPI->>Dep: Kiểm tra teacher
Dep-->>ClassAPI: current_teacher
ClassAPI->>ClassService: get_classes_by_teacher()
ClassService->>DB: SELECT class by teacher_id
DB-->>ClassService: class list
ClassService-->>ClassAPI: classes
ClassAPI-->>TeacherClassPage: danh sách lớp

alt Tạo hoặc sửa lớp
  Teacher->>TeacherClassPage: Nhập form lớp học
  TeacherClassPage->>ClassAPI: POST/PUT /classes
  ClassAPI->>ClassService: create_class()/update_class()
  ClassService->>DB: INSERT/UPDATE class
  ClassAPI-->>TeacherClassPage: class detail
else Quản lý sinh viên trong lớp
  Teacher->>TeacherClassPage: Mở modal sinh viên
  TeacherClassPage->>ClassAPI: GET /classes/{id}
  TeacherClassPage->>ClassAPI: GET /classes/{id}/available-students
  ClassAPI->>ClassService: get_class()/get_available_students()
  ClassService->>DB: SELECT class + students
  ClassService->>DB: SELECT available students
  ClassAPI-->>TeacherClassPage: class detail + available students
  TeacherClassPage->>ClassAPI: POST/DELETE /classes/{id}/students/{student_id}
  ClassAPI->>ClassService: add_student()/remove_student()
  ClassService->>DB: INSERT/DELETE class_student
  ClassAPI-->>TeacherClassPage: success
end
```

### SD-04: Teacher quản lý ngân hàng câu hỏi
```mermaid
sequenceDiagram
actor Teacher
participant QuestionPage as teacher/questions.vue
participant QuestionAPI as /questions
participant QuestionService
participant DB

Teacher->>QuestionPage: Mở trang câu hỏi
QuestionPage->>QuestionAPI: GET /questions
QuestionAPI->>QuestionService: get_questions()
QuestionService->>DB: SELECT questions
DB-->>QuestionService: question list
QuestionAPI-->>QuestionPage: danh sách câu hỏi

alt Tạo hoặc sửa câu hỏi
  Teacher->>QuestionPage: Nhập nội dung + đáp án
  QuestionPage->>QuestionAPI: POST/PUT /questions
  QuestionAPI->>QuestionService: create_question()/update_question()
  QuestionService->>DB: INSERT/UPDATE question
  QuestionAPI-->>QuestionPage: QuestionResponse
else Xóa câu hỏi
  Teacher->>QuestionPage: Xác nhận xóa
  QuestionPage->>QuestionAPI: DELETE /questions/{id}
  QuestionAPI->>QuestionService: delete_question()
  QuestionService->>DB: DELETE question
  QuestionAPI-->>QuestionPage: success
end
```

### SD-05: Teacher quản lý đề thi
```mermaid
sequenceDiagram
actor Teacher
participant ExamPage as teacher/exams.vue
participant ExamAPI as /exams
participant QuestionAPI as /questions
participant ClassAPI as /classes
participant ExamService
participant DB

Teacher->>ExamPage: Mở trang đề thi
ExamPage->>ExamAPI: GET /exams
ExamPage->>QuestionAPI: GET /questions
ExamPage->>ClassAPI: GET /classes
QuestionAPI-->>ExamPage: availableQuestions
ClassAPI-->>ExamPage: availableClasses
ExamAPI-->>ExamPage: exam list

alt Tạo đề
  Teacher->>ExamPage: Nhập thông tin + chọn câu hỏi/lớp
  ExamPage->>ExamAPI: POST /exams
  ExamAPI->>ExamService: create_exam()
  ExamService->>DB: INSERT exam
  ExamService->>DB: INSERT exam_allowed_class
  ExamService->>DB: INSERT exam_question
  ExamAPI-->>ExamPage: ExamResponse
else Sửa đề
  Teacher->>ExamPage: Mở modal sửa
  ExamPage->>ExamAPI: GET /exams/{id}
  ExamAPI-->>ExamPage: exam detail
  ExamPage->>ExamAPI: PUT /exams/{id}
  ExamAPI->>ExamService: update_exam()
  ExamService->>DB: UPDATE exam + relation
  ExamAPI-->>ExamPage: ExamResponse
else Xóa đề
  Teacher->>ExamPage: Xác nhận xóa
  ExamPage->>ExamAPI: DELETE /exams/{id}
  ExamAPI->>ExamService: delete_exam()
  ExamService->>DB: DELETE exam
  ExamAPI-->>ExamPage: success
end
```

### SD-06: Teacher xem thống kê kết quả và review bài làm
```mermaid
sequenceDiagram
actor Teacher
participant StatisticsPage as teacher/statistics.vue
participant ExamAPI as /exams
participant ResultAPI as /results/exam/{exam_id}
participant ReviewAPI as /results/{result_id}/review
participant ResultService
participant DB

Teacher->>StatisticsPage: Mở trang thống kê
StatisticsPage->>ExamAPI: GET /exams
ExamAPI-->>StatisticsPage: danh sách đề thi
StatisticsPage->>ResultAPI: GET /results/exam/{exam_id}
ResultAPI->>ResultService: get_exam_results_for_teacher()
ResultService->>DB: SELECT exam results + student info
DB-->>ResultService: result list
ResultAPI-->>StatisticsPage: bảng điểm chi tiết

loop Mỗi bài làm để tính thống kê độ khó
  StatisticsPage->>ReviewAPI: GET /results/{result_id}/review
  ReviewAPI->>ResultService: get_result_review()
  ResultService->>DB: SELECT result + details + questions
  DB-->>ResultService: review data
  ReviewAPI-->>StatisticsPage: question details
end

alt Xem chi tiết một bài làm
  Teacher->>StatisticsPage: Bấm "Xem đáp án"
  StatisticsPage->>ReviewAPI: GET /results/{result_id}/review
  ReviewAPI-->>StatisticsPage: review payload
end
```

### SD-07: Student xem danh sách bài thi và kiểm tra mật khẩu
```mermaid
sequenceDiagram
actor Student
participant StudentHome as student/index.vue
participant ExamListAPI as /exams/my-exams
participant PasswordAPI as /exams/{exam_id}/check-password
participant ExamService
participant DB

Student->>StudentHome: Mở trang bài thi
StudentHome->>ExamListAPI: GET /exams/my-exams
ExamListAPI->>ExamService: get_exams_for_student()
ExamService->>DB: SELECT exams by class
DB-->>ExamService: exam list
ExamListAPI-->>StudentHome: danh sách đề khả dụng

alt Đề không có mật khẩu
  Student->>StudentHome: Bấm "Vào thi"
  StudentHome-->>Student: Điều hướng /student/exam/{id}
else Đề có mật khẩu
  Student->>StudentHome: Nhập mật khẩu
  StudentHome->>PasswordAPI: POST check-password
  PasswordAPI->>ExamService: check_exam_password()
  ExamService->>DB: SELECT exam.password
  PasswordAPI-->>StudentHome: success/fail
  StudentHome-->>Student: Điều hướng vào bài thi nếu hợp lệ
end
```

### SD-08: Student làm bài thi, chống gian lận và nộp bài
```mermaid
sequenceDiagram
actor Student
participant ExamPage as student/exam/[id].vue
participant ExamAPI as /exams/{id}
participant QuestionAPI as /exams/{id}/questions
participant ResultAPI as /results/submit/{exam_id}
participant ResultService
participant DB

Student->>ExamPage: Mở bài thi
ExamPage->>ExamAPI: GET /exams/{id}
ExamPage->>QuestionAPI: GET /exams/{id}/questions
ExamAPI-->>ExamPage: exam detail
QuestionAPI-->>ExamPage: question list
ExamPage-->>Student: Hiển thị hướng dẫn + nút bắt đầu

Student->>ExamPage: Bắt đầu làm bài
ExamPage-->>ExamPage: Bật fullscreen + timer + anti-cheat listeners
loop Trong quá trình làm bài
  Student->>ExamPage: Chọn đáp án / chuyển câu / đánh dấu
  ExamPage-->>ExamPage: Cập nhật answers, flaggedQuestions
end

alt Vi phạm >= 3 lần hoặc bấm nộp
  ExamPage->>ResultAPI: POST answers
  ResultAPI->>ResultService: submit_exam()
  ResultService->>DB: INSERT exam_result
  ResultService->>DB: INSERT exam_result_detail
  ResultService->>DB: UPDATE total_score
  ResultAPI-->>ExamPage: kết quả nộp bài
  ExamPage-->>Student: Hiển thị điểm và trạng thái hoàn thành
end
```

### SD-09: Student xem lịch sử thi và review bài làm
```mermaid
sequenceDiagram
actor Student
participant HistoryPage as student/history.vue
participant HistoryAPI as /results/student/{student_id}
participant ExamListAPI as /exams/my-exams
participant ReviewAPI as /results/{result_id}/review
participant ResultService
participant DB

Student->>HistoryPage: Mở lịch sử thi
HistoryPage->>HistoryAPI: GET /results/student/{student_id}
HistoryPage->>ExamListAPI: GET /exams/my-exams
HistoryAPI-->>HistoryPage: danh sách kết quả
ExamListAPI-->>HistoryPage: danh sách đề để map tiêu đề + allow_view_answers

alt Đề cho phép xem đáp án
  Student->>HistoryPage: Bấm "Xem bài"
  HistoryPage->>ReviewAPI: GET /results/{result_id}/review
  ReviewAPI->>ResultService: get_result_review()
  ResultService->>DB: SELECT result + details + questions
  DB-->>ResultService: review data
  ReviewAPI-->>HistoryPage: review payload
  HistoryPage-->>Student: Hiển thị chi tiết bài làm
else Chưa được mở đáp án
  HistoryPage-->>Student: Hiển thị trạng thái "Chưa mở"
end
```

## 8) Ma trận chức năng theo vai trò

| Chức năng | Admin | Teacher | Student |
|---|---|---|---|
| Đăng nhập | X | X | X |
| Health check | X | X | X |
| Quản lý users | X |  |  |
| Quản lý lớp học |  | X |  |
| Quản lý học sinh trong lớp |  | X |  |
| Quản lý câu hỏi |  | X |  |
| Tạo/sửa/xóa đề |  | X |  |
| Xem đề của mình |  | X | X |
| Kiểm tra mật khẩu đề |  | X | X |
| Nộp bài thi |  |  | X |
| Xem lịch sử kết quả |  | X | X |
| Review bài làm |  | X | X |
| Sửa điểm/xóa kết quả |  | X |  |

## 9) Danh mục endpoint (để đối chiếu nhanh)

- `POST /login`
- `GET /`
- `POST /users`
- `GET /users`
- `GET /users/{user_id}`
- `PUT /users/{user_id}`
- `DELETE /users/{user_id}`
- `GET /classes`
- `POST /classes`
- `GET /classes/{class_id}`
- `PUT /classes/{class_id}`
- `DELETE /classes/{class_id}`
- `GET /classes/{class_id}/available-students`
- `POST /classes/{class_id}/students/{student_id}`
- `DELETE /classes/{class_id}/students/{student_id}`
- `POST /questions`
- `GET /questions`
- `GET /questions/{question_id}`
- `PUT /questions/{question_id}`
- `DELETE /questions/{question_id}`
- `GET /exams`
- `POST /exams`
- `GET /exams/my-exams`
- `GET /exams/{exam_id}`
- `PUT /exams/{exam_id}`
- `DELETE /exams/{exam_id}`
- `GET /exams/{exam_id}/questions`
- `POST /exams/{exam_id}/check-password`
- `POST /results/submit/{exam_id}`
- `GET /results/{result_id}`
- `GET /results/student/{student_id}`
- `GET /results/exam/{exam_id}`
- `GET /results/{result_id}/review`
- `PUT /results/{result_id}/score`
- `DELETE /results/{result_id}`
