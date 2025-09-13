# BKN1 Assessment System

ระบบประเมินผล BKN1 สำหรับการจัดการแบบประเมินและการกรอกข้อมูลแบบลำดับชั้น

## คุณสมบัติระบบ

### สถาปัตยกรรม
- **Frontend**: Vue.js 3 พร้อม Element Plus UI
- **Backend**: Flask REST API พร้อมการจัดการสิทธิ์ 
- **Database**: PostgreSQL พร้อมโครงสร้างแบบลำดับชั้น
- **BI Dashboard**: Metabase สำหรับการสร้างรายงาน
- **Reverse Proxy**: Nginx
- **Database Management**: PgAdmin

### ฟีเจอร์หลัก

#### การจัดการผู้ใช้
- ระบบ Login พร้อม 3 ประเภทผู้ใช้: Admin, Moderator, User
- การควบคุมสิทธิ์การเข้าถึงข้อมูลแบบละเอียด

#### การจัดการแบบประเมิน
- สร้างแบบประเมินพร้อมโครงสร้างแบบลำดับชั้น:
  - ประเด็น (Assessment Items)
  - ตัวชี้วัด (Indicators) 
  - รายการตัวชี้วัด (Indicator Items)
- ปีงบประมาณในรูปแบบพุทธศักราช
- การกำหนดสิทธิ์ผู้ใช้สำหรับแต่ละตัวชี้วัด
- สถานะแบบประเมิน: ร่าง (Draft) และเผยแพร่ (Published)

#### การกรอกข้อมูล
- ฟอร์มกรอกข้อมูลตามสิทธิ์ของผู้ใช้
- อัพโหลดรูปภาพประกอบ
- บันทึกข้อมูลแบบร่างและส่งข้อมูลสมบูรณ์
- ตรวจสอบความครบถ้วนของข้อมูลก่อนส่ง

#### รายงานและสรุปผล
- สรุปรายงานตามสิทธิ์การเข้าถึง
- แสดงสถานะการกรอกข้อมูลของแต่ละผู้ใช้
- เชื่อมต่อ Metabase Dashboard
- ดูรูปภาพที่อัพโหลด

## การติดตั้งและเรียกใช้งาน

### ข้อกำหนดเบื้องต้น
- Docker และ Docker Compose
- Node.js 18+ (สำหรับการพัฒนา)
- Python 3.11+ (สำหรับการพัฒนา)

### การเรียกใช้ด้วย Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd bkn1

# เรียกใช้ทั้งระบบ
docker-compose up -d

# ดูสถานะ services
docker-compose ps

# ดู logs
docker-compose logs -f
```

### การเข้าถึงระบบ

- **แอปพลิเคชันหลัก**: http://localhost
- **PgAdmin**: http://localhost:5050
- **Metabase**: http://localhost:3001

### ผู้ใช้งานเริ่มต้น

- **Admin**: username: `admin`, password: `admin123`
- **Moderator**: username: `moderator`, password: `admin123` 
- **User**: username: `user1`, password: `admin123`

## โครงสร้างโปรเจค

```
bkn1/
├── docker-compose.yml          # Docker services configuration
├── nginx/
│   └── nginx.conf             # Nginx reverse proxy config
├── database/
│   └── init/
│       └── 01-schema.sql      # Database schema
├── backend/                   # Flask API
│   ├── app.py                # Main application
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Backend container
│   └── app/
│       ├── models/          # Database models
│       ├── routes/          # API endpoints
│       └── utils/           # Utility functions
└── frontend/                # Vue.js application
    ├── package.json         # Node.js dependencies
    ├── Dockerfile          # Frontend container
    ├── vite.config.js      # Build configuration
    └── src/
        ├── components/     # Vue components
        ├── views/         # Page components
        ├── router/        # Route configuration
        ├── store/         # Vuex state management
        └── services/      # API service calls
```

## การพัฒนา

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Management

เข้าถึง PgAdmin ที่ http://localhost:5050
- Email: admin@bkn1.local
- Password: admin123

เพิ่ม server connection:
- Host: postgres
- Port: 5432
- Database: bkn1_db
- Username: bkn1_user
- Password: bkn1_password

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - เข้าสู่ระบบ
- `GET /api/auth/profile` - ข้อมูลผู้ใช้ปัจจุบัน
- `GET /api/auth/users` - รายการผู้ใช้ (Admin/Moderator)

### Assessment Endpoints
- `GET /api/assessments` - รายการแบบประเมิน
- `POST /api/assessments` - สร้างแบบประเมิน
- `GET /api/assessments/{id}` - ข้อมูลแบบประเมิน
- `PUT /api/assessments/{id}` - แก้ไขแบบประเมิน
- `DELETE /api/assessments/{id}` - ลบแบบประเมิน

### User Data Endpoints
- `GET /api/user-data/{indicator_item_id}` - ข้อมูลผู้ใช้
- `POST /api/user-data/{indicator_item_id}` - บันทึกข้อมูล
- `POST /api/user-data/{indicator_item_id}/upload` - อัพโหลดรูปภาพ
- `GET /api/user-data/report/{assessment_id}` - รายงานสรุป

## License

MIT License