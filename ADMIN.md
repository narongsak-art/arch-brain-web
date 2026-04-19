# Admin Guide · การจัดการ contributions

คู่มือสำหรับ admin (Narongsak) ในการดูแล community contributions.

## 🔐 Setup (ครั้งเดียว)

### 1. สร้าง GitHub Personal Access Token
1. เปิด https://github.com/settings/tokens
2. **Generate new token (classic)**
3. Scope: `repo` (หรือ `public_repo` ถ้า repo เป็น public)
4. Expiration: 90 วัน
5. Copy token · เก็บไว้ใช้ขั้นต่อไป

### 2. สร้าง admin passphrase
สุ่มสตริงยาว ≥ 32 chars · เช่นผ่าน:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. ใส่ secrets ใน Streamlit Cloud
- เปิด **app settings** → **Secrets**
- Paste:
```toml
[github]
token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxx"
repo = "narongsak-art/arch-brain-web"
branch = "main"
committer_name = "arch-brain contributor"
committer_email = "bot@arch-brain.local"

[admin]
token = "your-32-char-admin-passphrase-here"
```
- Save · app จะ restart

### 4. ทดสอบ
- เปิด `https://arch-brain-narongsak.streamlit.app/?admin=<your-admin-token>`
- ควรเห็น **👮 Admin Moderation** panel

---

## 🔄 Daily workflow

```
┌─ ผู้ใช้ทั่วไป ──────────────────────────────────────────────┐
│  1. เขียน contribution ในเว็ป (tab 💡 ช่วยเติม)            │
│  2. คลิก ✨ AI ช่วยจัดระเบียบ  (optional)                    │
│  3. คลิก 🚀 ส่งขึ้น GitHub                                  │
│     → commit ใน contributions/{type}/...                    │
└──────────────────────────────────────────────────────────────┘

┌─ Admin (คุณ) ────────────────────────────────────────────────┐
│  4. เปิด ?admin=<token>                                       │
│  5. ดู queue (กรอง status = pending + submitted)              │
│  6. ตัดสินใจ:                                                 │
│     · ✅ Approve           → update commit status=approved    │
│     · ❌ Reject (+ reason) → update commit status=rejected    │
│     · ✏ Edit + Approve    → แก้ title/body/cat แล้ว approve  │
└──────────────────────────────────────────────────────────────┘

┌─ Automation (GitHub Actions) ────────────────────────────────┐
│  7. .github/workflows/promote-approved.yml                    │
│     → detect approved · convert JSON → .md                    │
│     → commit ลง wiki-mirror/wiki/                             │
│  8. .github/workflows/rebuild-kg.yml                          │
│     → detect wiki-mirror change · run build_kg.py             │
│     → commit ลง kg-compact.json + full-knowledge.md           │
│  9. Streamlit Cloud auto-redeploy                             │
│     → AI ใช้ knowledge ใหม่ในการวิเคราะห์ทันที                │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎛 Admin UI · sections

### Metrics row
- **รวม** (total)
- **🟡 pending** (ยังไม่ได้ push จาก session)
- **🟠 submitted** (push แล้วรอตรวจ)
- **🟢 approved** (ผ่านแล้ว)
- **🔴 rejected** (ปฏิเสธพร้อมเหตุผล)

### Filter
Multi-select โดย default เลือก `pending` + `submitted`

### Per entry
- ดู body · category · type · AI suggestions · author
- **3 tabs:**
  - ✅ Approve — optional note · กด commit
  - ❌ Reject — required reason · กด commit
  - ✏ Edit + Approve — แก้ title/body/category แล้ว approve

### Controls
- 🔄 Refresh (บังคับ bust cache 60s)
- 🚪 Exit admin mode

---

## 📂 File paths

Contributions ใน GitHub repo:
```
contributions/
├── corrections/   # 📝 แก้ไข/ทักท้วง
├── proposals/     # 💡 เสนอเรื่องใหม่
├── cases/         # 🏗 เคสจริง
└── questions/     # ❓ คำถาม
```

ตัวอย่างชื่อไฟล์:
```
contributions/cases/2026-04-20_บ้าน-200-ตรม-นนท_abc12345.json
```

### Schema ต่อไฟล์
```json
{
  "id": "abc12345",
  "timestamp": "2026-04-20T15:30:00",
  "type": "case",
  "category": "renovation",
  "title": "...",
  "body": "...",
  "author": "somchai",
  "related_pages": [],
  "status": "approved",
  "ai_suggestions": {...},
  "approved_at": "2026-04-20T16:00:00",
  "approval_note": "ข้อมูลครบ · ผ่าน"
}
```

---

## 🧪 Local ingest (manual path)

ถ้าไม่ต้องการใช้ GitHub Actions · ยังสามารถทำ local ingest ได้:

```bash
cd E:/Narongsakb/arch-brain-web
git pull                                      # ดึง approved entries ล่าสุด
python scripts/ingest_contributions.py \
    --vault E:/Narongsakb/NarongsakBIM \
    --dry-run                                 # preview ก่อน
python scripts/ingest_contributions.py \
    --vault E:/Narongsakb/NarongsakBIM        # เขียนจริง + regen KG
git add kg-compact.json full-knowledge.md
git commit -m "ingest: N approved community contributions"
git push
```

**ข้อดีของ local:** เขียนลง vault จริงของคุณ (`NarongsakBIM`) · ไม่ใช่ mirror
**ข้อเสีย:** ต้อง manual · ต้องทำทุกครั้ง

---

## 🚨 Troubleshooting

### "ยังไม่ได้ตั้งค่า GitHub secrets"
→ ใส่ `[github]` block ใน secrets ตาม §Setup

### PAT ไม่ถูกต้อง หรือหมดอายุ
→ Generate ใหม่ที่ github.com/settings/tokens · อัปเดต secrets

### "ไฟล์มีอยู่แล้ว" (422)
→ entry id ซ้ำ · คงเป็น bug · แจ้งผู้ developer

### Admin panel ขึ้น error "❌ GitHub sync ยังไม่ได้ตั้งค่า"
→ `[github]` block ขาด · ต้องใส่ก่อน admin มันใช้ได้

### Token ใน URL leak ได้ไหม?
→ URL fragments (`#`) + path/query params ถูก log ใน access logs ของ browser + server · **ไม่ควรส่ง URL นี้ให้ใคร** · ถ้าหลุดให้ rotate token ทันที

### ถ้าลืม passphrase
→ ไป Streamlit Cloud → Secrets → แก้ `admin.token` เป็นค่าใหม่

---

## 🔒 Security notes

- **PAT มีสิทธิ์เขียน repo** · รักษาเหมือนรหัส
- **Rotate token ทุก 90 วัน**
- **Admin token แยกจาก PAT** · ถ้าอันนึง leak อีกอันยังปลอดภัย
- **GitHub Action permissions:** `contents: write` เฉพาะ (ไม่ access secrets)
- **Public audit trail:** ทุก approval/rejection เป็น commit ที่ดูย้อนหลังได้
