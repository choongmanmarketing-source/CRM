# Restaurant CRM (Vercel-compatible, fallback-safe)

เวอร์ชันนี้แก้ปัญหา "ใช้งานไม่ได้" จาก path บน Vercel ที่อาจต่างกันในแต่ละโปรเจกต์:

- รองรับ API ทั้ง `/<endpoint>` และ `/api/<endpoint>`
- หน้าแรก `/` แสดง UI เสมอ (ไม่ใช่ JSON อย่างเดียว)

## ใช้งาน

- หน้าเว็บ: `/`
- Health: `/health` หรือ `/api/health`
- API Docs: `/docs` (และบาง deployment อาจใช้ `/api/docs`)

## API

- `POST /customers` หรือ `POST /api/customers`
- `GET /customers` หรือ `GET /api/customers`
- `GET /customers/{phone}` หรือ `GET /api/customers/{phone}`
- `POST /purchase` หรือ `POST /api/purchase`

## หมายเหตุ

- SQLite บน Vercel เป็น ephemeral storage
- ถ้าใช้งานจริง แนะนำย้าย DB ไป PostgreSQL/Supabase/Neon

## ทดสอบ

```bash
python -m pytest -q
```
