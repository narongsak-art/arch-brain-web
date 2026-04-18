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
2. Download เป็น `.json`
3. (future) GitHub API push → commit ลง folder นี้
4. Admin review → ถ้า OK · แปลงเป็น `.md` ใน `wiki/` + run `scripts/build_kg.py`
