# 📦 Contributions (กล่องที่ 2: กล่องรอเข้า)

โฟลเดอร์นี้เก็บ "ของที่เพื่อนเขียน" ก่อนที่จะผ่านการตรวจแล้วเข้าสมุดใหญ่ (`wiki/`)

## โครงสร้าง

```
contributions/
├── README.md              # ไฟล์นี้
├── corrections/            # 📝 แก้ไข · ทักท้วงข้อผิด
├── proposals/              # 💡 เสนอเรื่องใหม่
├── cases/                  # 🏗 เคสจริง
└── questions/              # ❓ คำถาม
```

## Schema (ไฟล์ .json แต่ละไฟล์)

```json
{
  "id": "uuid",
  "timestamp": "2026-04-18T15:30:00",
  "type": "correction | proposal | case | question",
  "category": "law-zoning",
  "title": "ข้อความสั้นๆ",
  "body": "เนื้อหาแบบ markdown",
  "author": "ชื่อผู้ส่ง (ไม่บังคับ)",
  "related_pages": ["wiki/concepts/ระยะร่น", "..."],
  "status": "pending | approved | rejected"
}
```

## 12 หัวข้อ (categories)

| # | Key | หัวข้อ |
|---|-----|--------|
| 1 | `law-zoning` | 🏛 กฎหมายและผังเมือง |
| 2 | `structure` | 🔧 โครงสร้างและวัสดุ |
| 3 | `mep` | ⚡ ระบบงานอาคาร (ไฟฟ้า-ประปา-แอร์) |
| 4 | `design` | 🎨 การออกแบบและสัดส่วน |
| 5 | `thai-culture` | 🪷 วัฒนธรรมและวิถีไทย |
| 6 | `fengshui` | ☯ ฮวงจุ้ย |
| 7 | `landscape` | 🌳 ภูมิสถาปัตย์และสวน |
| 8 | `sustainability` | 🌱 ความยั่งยืนและพลังงาน |
| 9 | `renovation` | 🏗 รีโนเวทและซ่อมแซม |
| 10 | `cost` | 💰 งบประมาณและต้นทุน |
| 11 | `smart-home` | 🤖 สมาร์ทโฮมและเทคโนโลยี |
| 12 | `bim-tools` | 📐 BIM และเครื่องมือออกแบบ |

## Flow

1. User กรอก form ในเว็ป → save เข้า session
2. ✅ **Phase 3:** คลิก "🚀 ส่งขึ้น GitHub" → commit อัตโนมัติผ่าน GitHub API
3. ⏳ **Phase 4 (next):** admin review queue · approve → แปลงเป็น `.md` ใน `wiki/`
4. ⏳ **Phase 5 (next):** GitHub Action run `scripts/build_kg.py` · auto-deploy

## 🌐 เปิด GitHub push (Phase 3)

เพิ่มไฟล์ `.streamlit/secrets.toml` ที่ repo root (หรือ Streamlit Cloud UI):

```toml
[github]
token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
repo = "narongsak-art/arch-brain-web"
branch = "main"
committer_name = "arch-brain contributor"
committer_email = "bot@arch-brain.local"
```

### สร้าง Personal Access Token (PAT)

1. ไปที่ https://github.com/settings/tokens
2. "Generate new token" (classic)
3. Scope: **repo** (หรือ `public_repo` ถ้า repo เป็น public)
4. Expiration: 90 วัน แนะนำ
5. Copy token ไปใส่ใน `token =` ด้านบน

### File path convention

แต่ละ contribution ที่ push จะกลายเป็นไฟล์ใน:
```
contributions/{folder}/{YYYY-MM-DD}_{slug}_{id}.json
```

โดย `{folder}` แปลงจาก type:
- `correction` → `corrections/`
- `proposal` → `proposals/`
- `case` → `cases/`
- `question` → `questions/`

### Commit message format

```
community: {type} · {title} (by {author})
```

### Security notes

- **อย่า commit secrets.toml ขึ้น Git** · เพิ่มใน `.gitignore` (`.streamlit/secrets.toml`)
- **PAT ควรหมดอายุทุก 90 วัน** · rotate regularly
- PAT มี scope แค่ `repo` ของคุณเอง · ไม่ใช่ admin token
- ถ้า leak · ยกเลิกที่ github.com/settings/tokens
