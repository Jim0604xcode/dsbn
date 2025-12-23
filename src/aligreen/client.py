
from alibabacloud_green20220302.client import Client
from alibabacloud_tea_openapi.models import Config
from alibabacloud_green20220302 import models as green_models
import json

from src.aligreen.schemas import TextSafetyCheckResult
from src.loggerServices import log_error, log_info
from src.exceptions import GeneralErrorExcpetion
from src.aligreen.constants import (
    SERVICE_QUERY_SECURITY_CHECK_INTL,
    STATUS_SUCCESS,
)


class AliGreenClient:
    """
    AliGreen client (Green SDK) 
    Provide text safety check, sensitive word detection, etc.
    """
    
    def __init__(
        self, 
        access_key_id: str,
        access_key_secret: str,
        region_id: str = 'ap-southeast-1',
        endpoint: str = 'green-cip.ap-southeast-1.aliyuncs.com',
        connect_timeout: int = 1000,
        read_timeout: int = 3000
    ):

        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region_id = region_id
        self.endpoint = endpoint
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.client = None
        self._init_client()
    
    def _init_client(self):
        try:
            config = Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                connect_timeout=self.connect_timeout,
                read_timeout=self.read_timeout,
                region_id=self.region_id,
                endpoint=self.endpoint
            )
            # log_info(f"AliGreen client config: {config}")
            self.client = Client(config)
            # log_info("AliGreen client initialized successfully")
        except Exception as e:
            log_error(f"Failed to initialize AliGreen client: {e}")
            raise GeneralErrorExcpetion(details=f"Failed to initialize AliGreen client: {e}")
    

    def check_text_safety(
        self, 
        content: str,
        service: str = SERVICE_QUERY_SECURITY_CHECK_INTL
    ) -> TextSafetyCheckResult:
        """
        Check text safety (simplified version)
        
        :param content: Text content to be checked
        :param service: Detection service type
        :return: Simplified detection result
        
        Return format:
        
        {
            'is_safe': True/False,
            'labels': 'normal' or 'risk',
            'reason': 'reason for the result',
            'suggestion': 'pass'/'review'/'block',
            'confidence': 0.95,
            'raw_response': {...}  # raw response
        }
        """
        try:
            self._check_client()
            request = self._build_request(content, service)
            response = self._send_and_check_response(request)
            code, message, request_id, data = self._parse_response_body(getattr(response, 'body', None))
            is_safe, risk_level, attack_level, sensitive_level, suggestion, labels = self._analyze_risk_levels(data)
            confidence = self._calculate_confidence(data, is_safe)
            reason = self._extract_reason(data, is_safe)
            result = self._pack_final_result(is_safe, labels, reason, suggestion, confidence, code, message, request_id, data, risk_level, attack_level, sensitive_level)
            # log_info(
            #     f"AliGreen check completed: is_safe={is_safe}, risk={risk_level}, attack={attack_level}, sensitive={sensitive_level}"
            # )
            return result

        except GeneralErrorExcpetion:
            raise
        except Exception as e:
            error_msg = f"Error during text safety check: {e}"
            log_error(error_msg)
            raise GeneralErrorExcpetion(details=error_msg)
    
    def get_client(self):
        """Return the underlying SDK client (for advanced operations)"""
        return self.client

    def _check_client(self):
        if not self.client:
            raise GeneralErrorExcpetion(details="AliGreen client not initialized")

    def _build_request(self, content, service):
        service_parameters = {
            'content': content
        }
        return green_models.TextModerationPlusRequest(
            service=service,
            service_parameters=json.dumps(service_parameters)
        )

    def _send_and_check_response(self, request):
        response = self.client.text_moderation_plus(request)
        if response.status_code != STATUS_SUCCESS:
            error_msg = (
                f"AliGreen API error: status={response.status_code}, "
                f"body={getattr(response, 'body', None)}"
            )
            log_error(error_msg)
            raise GeneralErrorExcpetion(details=error_msg)
        return response

    def _parse_response_body(self, body):
        code = getattr(body, 'code', None) or getattr(body, 'Code', None)
        message = getattr(body, 'msg', None) or getattr(body, 'Message', None)
        request_id = getattr(body, 'request_id', None) or getattr(body, 'RequestId', None)
        data_raw = getattr(body, 'data', None) or getattr(body, 'Data', None)

        # Parse Data which may be a JSON string
        data = None
        if isinstance(data_raw, str):
            try:
                data = json.loads(data_raw)
            except json.JSONDecodeError:
                data = None
        elif isinstance(data_raw, dict):
            data = data_raw
        else:
            try:
                data = {
                    'Result': getattr(data_raw, 'Result', None) or getattr(data_raw, 'result', None),
                    'SensitiveResult': getattr(data_raw, 'SensitiveResult', None) or getattr(data_raw, 'sensitive_result', None),
                    'AttackResult': getattr(data_raw, 'AttackResult', None) or getattr(data_raw, 'attack_result', None),
                    'RiskLevel': getattr(data_raw, 'RiskLevel', None) or getattr(data_raw, 'risk_level', None),
                    'SensitiveLevel': getattr(data_raw, 'SensitiveLevel', None) or getattr(data_raw, 'sensitive_level', None),
                    'AttackLevel': getattr(data_raw, 'AttackLevel', None) or getattr(data_raw, 'attack_level', None),
                }
            except Exception:
                data = None
        if data is None:
            data = {}
        return code, message, request_id, data

    def _analyze_risk_levels(self, data):
        risk_level = str(data.get('RiskLevel', '') or '').lower()
        attack_level = str(data.get('AttackLevel', '') or '').lower()
        sensitive_level = str(data.get('SensitiveLevel', '') or '').upper()

        is_risk_none = risk_level == 'none'
        is_attack_none = attack_level == 'none'
        is_sensitive_s0 = sensitive_level == 'S0'
        is_safe = is_risk_none and is_attack_none and is_sensitive_s0

        if risk_level == 'high':
            suggestion = 'block'
        elif risk_level in ('medium', 'low'):
            suggestion = 'review'
        else:
            suggestion = 'pass'

        from .constants import LABEL_NORMAL, LABEL_RISK
        labels = LABEL_NORMAL if is_safe else LABEL_RISK

        return is_safe, risk_level, attack_level, sensitive_level, suggestion, labels

    def _calculate_confidence(self, data, is_safe):
        def _max_conf(items):
            max_c = 0.0
            if isinstance(items, list):
                for it in items:
                    try:
                        c = float(it.get('Confidence', 0.0))
                        if c > max_c:
                            max_c = c
                    except Exception:
                        continue
            return max_c
        max_conf = 0.0
        max_conf = max(max_conf, _max_conf(data.get('Result')))
        max_conf = max(max_conf, _max_conf(data.get('AttackResult')))
        if max_conf > 0:
            confidence = round(max_conf / 100.0, 4)
        else:
            confidence = 1.0 if is_safe else 0.5
        return confidence

    def _extract_reason(self, data, is_safe):
        reason = ''
        for key in ('AttackResult', 'Result', 'SensitiveResult'):
            arr = data.get(key)
            if isinstance(arr, list) and len(arr) > 0:
                desc = arr[0].get('Description') if isinstance(arr[0], dict) else None
                if desc:
                    reason = desc
                    break
        return reason

    def _pack_final_result(self, is_safe, labels, reason, suggestion, confidence, code, message, request_id, data, risk_level, attack_level, sensitive_level):
        from .constants import SUGGESTION_PASS, SUGGESTION_REVIEW, SUGGESTION_BLOCK
        if suggestion == 'pass':
            suggestion_enum = SUGGESTION_PASS
        elif suggestion == 'review':
            suggestion_enum = SUGGESTION_REVIEW
        else:
            suggestion_enum = SUGGESTION_BLOCK
        raw_response = {
            'Code': code,
            'Data': data,
            'Message': message,
            'RequestId': request_id,
        }
        return TextSafetyCheckResult(
            is_safe=is_safe,
            labels=labels,
            reason=reason or ("result is safe" if is_safe else "result is not safe"),
            suggestion=suggestion_enum,
            confidence=confidence,
            raw_response=raw_response,
        )

