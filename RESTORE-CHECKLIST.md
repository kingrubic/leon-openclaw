# RESTORE-CHECKLIST.md

Checklist chuyển Leon sang máy mới.

## Mục tiêu

Khôi phục đầy đủ:
- memory
- skills
- script workflow
- cron backup snapshot
- GitHub backup flow
- Google Docs / Sheets working access
- cron chạy thật trong OpenClaw

## 1. Cài môi trường nền

Trên máy mới, cài và xác nhận:
- OpenClaw chạy được
- Git chạy được
- Python 3 hoạt động
- trình duyệt / browser runtime dùng cho automation nếu cần

Khuyến nghị kiểm tra nhanh:
```bash
openclaw status
python3 --version
git --version
```

## 2. Kéo repo backup về máy mới

```bash
cd ~/.openclaw
mkdir -p workspace
cd workspace
git clone https://github.com/kingrubic/leon-openclaw.git .
```

Nếu repo đã có sẵn:
```bash
cd /Users/admin/.openclaw/workspace
git pull origin main
```

## 3. Kiểm tra những gì đã được phục hồi từ GitHub

Sau khi pull, xác nhận có đủ:
- `memory/`
- `skills/`
- `cron-backup.json`
- các script daily-run
- `RESTORE-CHECKLIST.md`

Lưu ý:
- GitHub backup hiện **không tự khôi phục cron thật trong OpenClaw**
- GitHub backup hiện **không tự mang secret/token cục bộ** nếu các file secret không được commit

## 4. Phục hồi Google credentials

Cần kiểm tra và phục hồi các file Google credential đang dùng cho Docs/Sheets:
- `google-credentials/kenyaimmigration-org.oauth-client.json`
- `google-credentials/kenyaimmigration-org.tokens.json`

Nếu thiếu các file này, phải:
- copy từ máy cũ sang máy mới, hoặc
- đăng nhập OAuth lại để lấy token mới

Sau khi phục hồi, test quyền đọc/ghi Google Sheets / Docs.

## 5. Phục hồi GitHub auth cho backup tự động

Cần cấu hình lại GitHub credential trên máy mới để cron backup có thể push:

```bash
git config credential.helper osxkeychain
```

Sau đó đăng nhập/push thử với repo:
- `https://github.com/kingrubic/leon-openclaw`

Test nhanh:
```bash
cd /Users/admin/.openclaw/workspace
git push origin main
```

## 6. Phục hồi cron thật trong OpenClaw

`cron-backup.json` chỉ là snapshot để đối chiếu, không tự tạo lại cron chạy thật.

Hiện các cron chuẩn cần có:
- India eVisa daily report — `08:00` Asia/Saigon
- Sri Lanka ETA daily report — `08:15` Asia/Saigon
- Australia visa daily report — `08:30` Asia/Saigon
- Indonesia visa daily report — `08:45` Asia/Saigon
- Workspace GitHub backup — `00:00` Asia/Saigon

Sau khi sang máy mới, cần tạo lại các cron này trong OpenClaw.

## 7. Kiểm tra workbook cố định của từng nước

Đảm bảo workflow vẫn dùng đúng workbook cố định, không tạo file sheet mới ngoài ý muốn:
- India: workbook giá India hiện hành
- Sri Lanka: workbook Sri Lanka ETA hiện hành
- Australia: `Australia Visa - Official Tracker`
- Indonesia: `Indonesia Visa - Official Tracker`
- Summary tracker: `Tổng hợp báo cáo Visa`

## 8. Kiểm tra rule report đang áp dụng

Các rule nghiệp vụ quan trọng hiện đã được lưu trong skills:
- dùng 1 workbook cố định cho mỗi nước
- chỉ tạo / cập nhật tab ngày mới
- section lớn `1..8` phải là heading thật
- tên visa / stream chỉ bold, không dùng heading
- tách business changes và `TECHNICAL CHANGELOG`
- QA cuối phải điền file `Tổng hợp báo cáo Visa`
- tin nhắn hoàn thành chỉ gồm:
  1. Link tổng hợp
  2. Link docs
  3. Link sheet
  4. 1 câu tóm tắt ngắn

## 9. Test khôi phục tối thiểu

Sau khi setup máy mới, nên chạy 1 test nhỏ:
1. đọc được repo workspace
2. ghi được vào 1 Google Sheet test hoặc workbook thật
3. tạo được 1 Google Doc test
4. push được 1 commit test lên GitHub
5. tạo được 1 cron test trong OpenClaw

Nếu 5 bước này pass thì coi như restore gần hoàn chỉnh.

## 10. Ghi nhớ ngắn gọn

Kéo GitHub về sẽ phục hồi được phần:
- brain
- memory
- skills
- workflow

Nhưng vẫn phải phục hồi thêm:
- secret/token
- cron thật
- runtime/tooling cục bộ
- GitHub auth

## File mốc để kiểm tra nhanh

- `memory/2026-03-26.md`
- `memory/2026-03-27.md`
- `cron-backup.json`
- `skills/india-evisa-report-sync/`
- `skills/sri-lanka-eta-report-sync/`
- `skills/australia-visa-report-sync/`
- `run_indonesia_visa_trial_27mar26.py`

Nếu các file trên có mặt + Google/GitHub auth hoạt động + cron được tạo lại, Leon có thể tiếp tục làm việc gần như liền mạch trên máy mới.
