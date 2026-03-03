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
usecaseDiagram
actor Admin
actor Teacher
actor Student
actor Client as "Client/Monitoring"

rectangle "Quiz Exam System" {
  usecase U1 as "Đăng nhập"
  usecase U2 as "Kiểm tra trạng thái hệ thống"

  usecase U3 as "Quản lý người dùng"

  usecase U4 as "Quản lý lớp học"
  usecase U5 as "Quản lý học sinh trong lớp"

  usecase U6 as "Quản lý câu hỏi"

  usecase U7 as "Quản lý đề thi"
  usecase U8 as "Kiểm tra mật khẩu đề"
  usecase U9 as "Xem đề được phép thi"

  usecase U10 as "Nộp bài & chấm điểm"
  usecase U11 as "Xem lịch sử/kết quả"
  usecase U12 as "Review bài làm"
  usecase U13 as "Sửa điểm/Xóa kết quả"
}

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
usecaseDiagram
actor Teacher
actor Student

rectangle "Exam Module" {
  usecase E1 as "Tạo đề"
  usecase E2 as "Sửa đề"
  usecase E3 as "Xóa đề"
  usecase E4 as "Xem đề"
  usecase E5 as "Xem câu hỏi trong đề"
  usecase E6 as "Kiểm tra mật khẩu đề"
  usecase E7 as "Nộp bài"
  usecase E8 as "Review kết quả"
}

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

## 4) Mô hình lớp (Class Diagram)

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

User "1" --> "0..*" Class : creates
User "1" --> "0..*" Question : creates
Class "1" --> "0..*" ClassStudent
User "1" --> "0..*" ClassStudent : joins
Exam "1" --> "0..*" ExamQuestion
Question "1" --> "0..*" ExamQuestion
Exam "1" --> "0..*" ExamAllowedClass
Class "1" --> "0..*" ExamAllowedClass
Exam "1" --> "0..*" ExamResult
User "1" --> "0..*" ExamResult : takes
ExamResult "1" --> "0..*" ExamResultDetail
Question "1" --> "0..*" ExamResultDetail
```

## 5) Mô hình đối tượng (Object Snapshot)

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

## 6) Các biểu đồ tuần tự (Sequence Diagrams)

### SD-01: Đăng nhập
```mermaid
sequenceDiagram
actor User
participant FE as Frontend
participant AuthAPI as /login
participant UserService
participant DB

User->>FE: Nhập username/password
FE->>AuthAPI: POST /login
AuthAPI->>UserService: get_user_by_username()
UserService->>DB: SELECT user
DB-->>UserService: user
UserService-->>AuthAPI: verify_password()
AuthAPI-->>FE: access_token + user profile
FE-->>User: Đăng nhập thành công
```

### SD-02: Tạo người dùng
```mermaid
sequenceDiagram
actor Admin
participant FE
participant UserAPI as /users
participant UserService
participant DB

Admin->>FE: Nhập thông tin user mới
FE->>UserAPI: POST /users
UserAPI->>UserService: create_user()
UserService->>UserService: hash password
UserService->>DB: INSERT user
DB-->>UserService: created user
UserService-->>UserAPI: user
UserAPI-->>FE: UserResponse
```

### SD-03: Giáo viên tạo lớp và thêm học sinh
```mermaid
sequenceDiagram
actor Teacher
participant FE
participant ClassAPI as /classes
participant Dep as get_current_user
participant ClassService
participant DB

Teacher->>FE: Tạo lớp
FE->>ClassAPI: POST /classes
ClassAPI->>Dep: kiểm tra teacher
Dep-->>ClassAPI: current_teacher
ClassAPI->>ClassService: create_class()
ClassService->>DB: INSERT class
DB-->>ClassService: class
ClassService-->>ClassAPI: class detail
ClassAPI-->>FE: class detail

Teacher->>FE: Thêm học sinh
FE->>ClassAPI: POST /classes/{id}/students/{student_id}
ClassAPI->>ClassService: add_student()
ClassService->>DB: INSERT class_student
ClassAPI-->>FE: Student added
```

### SD-04: Tạo câu hỏi
```mermaid
sequenceDiagram
actor Teacher
participant FE
participant QuestionAPI as /questions
participant QuestionService
participant DB

Teacher->>FE: Nhập nội dung câu hỏi
FE->>QuestionAPI: POST /questions
QuestionAPI->>QuestionService: create_question()
QuestionService->>DB: INSERT question
DB-->>QuestionService: question
QuestionService-->>QuestionAPI: question
QuestionAPI-->>FE: QuestionResponse
```

### SD-05: Giáo viên tạo đề thi
```mermaid
sequenceDiagram
actor Teacher
participant FE
participant ExamAPI as /exams
participant Dep as get_current_user
participant ExamService
participant DB

Teacher->>FE: Nhập thông tin đề + class_ids + questions
FE->>ExamAPI: POST /exams
ExamAPI->>Dep: kiểm tra teacher
Dep-->>ExamAPI: current_user
ExamAPI->>ExamService: create_exam(exam_in, owner_id)
ExamService->>DB: INSERT exam
ExamService->>DB: INSERT exam_allowed_class*
ExamService->>DB: INSERT exam_question*
DB-->>ExamService: commit
ExamService-->>ExamAPI: exam
ExamAPI-->>FE: ExamResponse
```

### SD-06: Học sinh lấy danh sách đề được thi
```mermaid
sequenceDiagram
actor Student
participant FE
participant ExamAPI as /exams/my-exams
participant Dep as get_current_student
participant ExamService
participant DB

Student->>FE: Mở danh sách đề thi
FE->>ExamAPI: GET /exams/my-exams
ExamAPI->>Dep: xác thực student + lấy class_id
Dep-->>ExamAPI: current_student(class_id)
ExamAPI->>ExamService: get_exams_for_student(class_id)
ExamService->>DB: SELECT exam by allowed class
DB-->>ExamService: list exams
ExamService-->>ExamAPI: exams
ExamAPI-->>FE: danh sách đề
```

### SD-07: Kiểm tra mật khẩu đề
```mermaid
sequenceDiagram
actor Student
participant FE
participant ExamAPI as /exams/{exam_id}/check-password
participant ExamService
participant DB

Student->>FE: Nhập mật khẩu đề
FE->>ExamAPI: POST check-password
ExamAPI->>ExamService: check_exam_password()
ExamService->>DB: SELECT exam
DB-->>ExamService: exam/password
ExamService-->>ExamAPI: true/false
ExamAPI-->>FE: success hoặc lỗi mật khẩu
```

### SD-08: Học sinh nộp bài và chấm tự động
```mermaid
sequenceDiagram
actor Student
participant FE
participant ResultAPI as /results/submit/{exam_id}
participant Dep as get_current_user
participant ResultService
participant DB

Student->>FE: Bấm nộp bài
FE->>ResultAPI: POST answers
ResultAPI->>Dep: xác thực student
Dep-->>ResultAPI: current_user
ResultAPI->>ResultService: submit_exam(exam_id, student_id, answers)
ResultService->>DB: check exam + max_attempts
ResultService->>DB: INSERT exam_result
ResultService->>DB: SELECT exam_question list
loop answers
  ResultService->>DB: SELECT question + compare answer
  ResultService->>DB: INSERT exam_result_detail
end
ResultService->>DB: UPDATE total_score + COMMIT
ResultService-->>ResultAPI: result
ResultAPI-->>FE: điểm + thời gian
```

### SD-09: Giáo viên xem kết quả theo đề
```mermaid
sequenceDiagram
actor Teacher
participant FE
participant ResultAPI as /results/exam/{exam_id}
participant ResultService
participant DB

Teacher->>FE: Mở bảng điểm đề thi
FE->>ResultAPI: GET /results/exam/{exam_id}
ResultAPI->>ResultService: get_exam_results_for_teacher()
ResultService->>DB: check exam owner
ResultService->>DB: SELECT results + student info
DB-->>ResultService: list results
ResultService-->>ResultAPI: mapped response
ResultAPI-->>FE: danh sách kết quả
```

### SD-10: Review bài làm
```mermaid
sequenceDiagram
actor User as Student/Teacher
participant FE
participant ResultAPI as /results/{result_id}/review
participant ResultService
participant DB

User->>FE: Mở review
FE->>ResultAPI: GET review
ResultAPI->>ResultService: get_result_review(result_id)
ResultService->>DB: load result + exam + details + questions
DB-->>ResultService: review data
ResultService-->>ResultAPI: review DTO
ResultAPI->>ResultAPI: kiểm tra quyền theo role
ResultAPI-->>FE: câu hỏi + đáp án + đúng/sai
```

### SD-11: Cập nhật điểm thủ công
```mermaid
sequenceDiagram
actor Teacher
participant FE
participant ResultAPI as /results/{result_id}/score
participant ResultService
participant DB

Teacher->>FE: Nhập điểm mới
FE->>ResultAPI: PUT score
ResultAPI->>ResultService: update_result_score()
ResultService->>DB: UPDATE exam_result.total_score
DB-->>ResultService: result updated
ResultService-->>ResultAPI: result
ResultAPI-->>FE: xác nhận cập nhật
```

### SD-12: Xóa kết quả thi
```mermaid
sequenceDiagram
actor Teacher
participant FE
participant ResultAPI as /results/{result_id}
participant ResultService
participant DB

Teacher->>FE: Yêu cầu xóa kết quả
FE->>ResultAPI: DELETE /results/{result_id}
ResultAPI->>ResultService: delete_result()
ResultService->>DB: DELETE exam_result_detail
ResultService->>DB: DELETE exam_result
DB-->>ResultService: success
ResultService-->>ResultAPI: true
ResultAPI-->>FE: Result deleted
```

## 7) Ma trận chức năng theo vai trò

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

## 8) Danh mục endpoint (để đối chiếu nhanh)

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
