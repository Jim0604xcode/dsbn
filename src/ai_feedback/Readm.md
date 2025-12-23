# AI Feedback System

## Overview
The AI feedback system provides emotional support and guidance for users' life moment posts when their emotion rate is below 0.

## User Flow

### 1. Trigger Condition
- Display AI feedback button when post emotion rate < 0
- Button text: **"Souli 密語 💝 聽聽 💞"**

### 2. User Consent Dialog
When user clicks the button, show consent dialog:

**Message:**
> "Souli (您的AI密友) 想聆聽您的心聲，幫您看見一點光亮。為了讓 Souli 更好理解您，我們需要傳送您的貼文內容給系統分析。💛 請先確認內文沒有密碼、銀行帳戶或個人資料。"

**Buttons:**
- Agree: **"我明白並同意，請 Souli 幫我"**
- Disagree: **"我想先編輯一下"**

### 3. Response Scenarios

#### ✅ Success (Normal Case)
- Display AI feedback content
- Show 🛟 icon at bottom right corner

#### ⚠️ High Risk Case (AI detects serious situation)
- Display AI feedback content
- Show additional warning: **"請立即按下救生圈，尋找專業協助與緊急支援熱線。"**
- Show 🛟 icon at bottom right corner

#### 🚨 Safeguard Error
- Show message: **"我們察覺到你的內容或許涉及需要更即時支援的情緒狀況。請立即按下右下角的救生圈，尋找專業協助與緊急支援熱線。"**
- Show 🛟 icon at bottom right corner

#### ❌ Other Errors
- Show message: **"分析你的人生經歷時發生錯誤，請稍後再試。"**

## Technical Implementation

### API Endpoint
```
GET /ai_feedback/generate_ai_feedback/life_moment/{post_id}
```

### Response Status Codes
- `COMPLETED`: Normal success case
- `ERROR_SAFEGUARD`: Content flagged by safety system
- `ERROR_MASKING`: PII masking failed
- `ERROR_AI_FEEDBACK`: AI service failed
- `ERROR_OTHER`: General error
- `NA`: AI feedback not available for this post
