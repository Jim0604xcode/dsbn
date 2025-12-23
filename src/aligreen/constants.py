"""
Alicloud Green (Content Security) constants
"""

# Detection service type
SERVICE_QUERY_SECURITY_CHECK_INTL = "query_security_check_intl" 
SERVICE_TEXT_MODERATION = "text_moderation" 
SERVICE_CHAT_DETECTION = "chat_detection" 

# Response status code
STATUS_SUCCESS = 200

# Audit result labels (only keep normal / risk for existing usage scenarios)
LABEL_NORMAL = "normal"  # Normal
LABEL_RISK = "risk"  # Risk

# Suggested actions
SUGGESTION_PASS = "pass"  # Pass
SUGGESTION_REVIEW = "review"  # Review
SUGGESTION_BLOCK = "block"  # Block

