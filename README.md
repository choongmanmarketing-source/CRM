# Restaurant CRM (Vercel Ready)

ระบบ CRM ร้านอาหารที่รองรับการสะสมแต้ม และเปิดใช้งานบน **Vercel** ได้ผ่าน REST API

## ฟีเจอร์

- เพิ่มลูกค้า
- บันทึกยอดซื้อและคำนวณแต้ม
- ใช้แต้มเป็นส่วนลด
- ดูข้อมูลลูกค้าและระดับสมาชิก
- Deploy บน Vercel ได้ทันที

## โครงสร้างที่รองรับ Vercel

- `api/index.py` = FastAPI entrypoint สำหรับ Vercel Serverless Function
- `vercel.json` = กำหนด route ให้เปิดโดเมนแล้ววิ่งเข้า API
- `crm.py` = business logic และ SQLite persistence

## Deploy บน Vercel

1. Push โค้ดขึ้น GitHub
2. Import โปรเจกต์ใน Vercel
3. Vercel จะใช้ `vercel.json` และ build `api/index.py` อัตโนมัติ
4. เปิด URL แล้วทดสอบได้ทันที:
   - `GET /`
   - `GET /docs`

## API หลัก

### สร้างลูกค้า

`POST /customers`

```json
{
  "name": "Mint",
  "phone": "0812345678"
}
```

### บันทึกการซื้อ

`POST /purchase`

```json
{
  "phone": "0812345678",
  "amount": 459,
  "earn_rate": 10,
  "use_points": 0
}
```

### ดูลูกค้าทั้งหมด

`GET /customers`

### ดูลูกค้ารายคน

`GET /customers/{phone}`

## หมายเหตุสำคัญเรื่องข้อมูลบน Vercel

SQLite บน Serverless จะอยู่ในพื้นที่ชั่วคราว (ephemeral) และอาจไม่คงอยู่ถาวรข้ามการ deploy/scale
ถ้าต้องการใช้งาน production จริง ควรเปลี่ยนไปใช้ฐานข้อมูลภายนอก เช่น PostgreSQL, Supabase, Neon หรือ PlanetScale

## ทดสอบในเครื่อง

```bash
python -m pytest -q
```
