# 📧 Email 功能配置說明

## 概述
本系統支援自動發送電影票券Email功能，包含票券資訊和QR碼圖片。

## 當前狀態
- ✅ 模擬模式：Email內容會顯示在控制台，不會實際發送
- 🔧 實際發送：需要配置SMTP伺服器

## 配置步驟

### 1. Gmail 設定（推薦）

#### 步驟 1：啟用兩步驟驗證
1. 登入 Google 帳戶
2. 前往「安全性」設定
3. 啟用「兩步驟驗證」

#### 步驟 2：產生應用程式密碼
1. 在「安全性」設定中找到「應用程式密碼」
2. 選擇「郵件」和「其他（自訂名稱）」
3. 輸入名稱（如：Movie Ticket System）
4. 複製產生的16位元密碼

#### 步驟 3：修改程式碼
在 `app.py` 中找到以下設定並修改：

```python
SENDER_EMAIL = "your-email@gmail.com"  # 改為你的Gmail
SENDER_PASSWORD = "your-app-password"  # 改為應用程式密碼
```

### 2. 啟用實際發送
取消註解 `app.py` 中的以下程式碼：

```python
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"✅ Email成功發送到 {email}")
except Exception as smtp_error:
    print(f"❌ SMTP發送失敗: {smtp_error}")
```

### 3. 其他郵件服務商設定

#### Outlook/Hotmail
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
```

#### Yahoo Mail
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
```

#### 自架SMTP伺服器
```python
SMTP_SERVER = "your-smtp-server.com"
SMTP_PORT = 587  # 或 465 (SSL)
```

## Email 內容特色

### 🎨 美觀設計
- 漸層標題背景
- 票券資訊卡片式設計
- 響應式佈局

### 📱 QR碼整合
- 內嵌QR碼圖片
- 自動附加到Email中
- 支援所有郵件客戶端

### 📋 完整資訊
- 票券編號
- 電影名稱
- 座位號碼
- 購買時間
- 重要提醒事項

## 安全性注意事項

1. **不要將密碼寫在程式碼中**
   - 使用環境變數
   - 或使用配置檔案

2. **使用應用程式密碼**
   - 不要使用主要密碼
   - 定期更換應用程式密碼

3. **限制發送頻率**
   - 避免被標記為垃圾郵件
   - 遵守SMTP服務商限制

## 故障排除

### 常見錯誤

1. **Authentication failed**
   - 檢查Email和密碼是否正確
   - 確認已啟用兩步驟驗證
   - 確認使用應用程式密碼

2. **Connection refused**
   - 檢查SMTP伺服器和端口
   - 確認網路連線正常

3. **SSL/TLS error**
   - 確認使用正確的端口
   - 檢查伺服器SSL設定

### 測試方法

1. 先使用模擬模式測試
2. 確認Email內容正確
3. 再啟用實際發送

## 進階功能

### 自訂Email模板
可以修改 `send_ticket_email` 函數中的HTML內容來自訂Email樣式。

### 多語言支援
可以根據使用者語言設定發送不同語言的Email。

### 附件支援
除了QR碼，還可以附加其他檔案（如電影海報、場次表等）。 