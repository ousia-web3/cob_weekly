# -*- coding: utf-8 -*-
"""Bedrock InvokeModel 실패 시 DevOps/IAM 담당자에게 전달하기 좋은 메시지 생성."""

from __future__ import annotations

from typing import Any, Optional


def bedrock_invoke_failure_hint(
    exc: BaseException,
    *,
    bedrock_region: str,
    model_id: str,
    caller_arn: Optional[str] = None,
    operation: str = "bedrock:InvokeModel",
) -> str:
    """AWS 예외 정보와 IAM/콘솔 안내를 한 블록으로 만든다."""
    lines: list[str] = []

    code: Optional[str] = None
    msg: Optional[str] = None
    request_id: Optional[str] = None
    http_status: Optional[int] = None

    try:
        from botocore.exceptions import ClientError

        if isinstance(exc, ClientError):
            resp: dict[str, Any] = exc.response or {}
            err = resp.get("Error") or {}
            code = err.get("Code")
            msg = err.get("Message")
            meta = resp.get("ResponseMetadata") or {}
            request_id = meta.get("RequestId")
            http_status = meta.get("HTTPStatusCode")
    except Exception:
        pass

    lines.append("[요약]")
    lines.append(f"- 사용 리전(소스 리전): {bedrock_region}")
    lines.append(f"- 호출 modelId: {model_id}")
    lines.append(f"- 필요 API: {operation}")
    if caller_arn:
        lines.append(f"- 현재 IAM principal: {caller_arn}")
    if code:
        lines.append(f"- AWS Error code: {code}")
    if msg:
        lines.append(f"- AWS Message: {msg}")
    if request_id:
        lines.append(f"- x-amzn-RequestId: {request_id}")
    if http_status:
        lines.append(f"- HTTP status: {http_status}")
    lines.append(f"- 로컬 예외 타입: {type(exc).__name__}: {exc}")

    lines.append("")
    lines.append("[DevOps / IAM — 권한 부여 시 참고]")
    lines.append("1) IAM 정책에 최소한 다음이 포함되는지 확인:")
    lines.append(f'   Action: "{operation}"')
    lines.append(
        "   Resource (STS의 Account로 ACCOUNT_ID 치환, modelId 그대로 사용):"
    )
    lines.append(
        f"     arn:aws:bedrock:{bedrock_region}:ACCOUNT_ID:inference-profile/"
        f"{model_id}"
    )
    lines.append(
        "   정책 예시 (한 줄 Statement): "
        '{"Effect":"Allow","Action":"bedrock:InvokeModel","Resource":"arn:aws:bedrock:'
        + bedrock_region
        + f':<ACCOUNT_ID>:inference-profile/{model_id}"'
        + "}"
    )
    lines.append(
        "   일부 환경에서는 foundation-model ARN 추가가 필요할 수 있음 → IAM 정책 시뮬레이터로 "
        "InvokeModel 거부 원인 확인."
    )
    lines.append("2) Organizations SCP나 Permission boundary가 위 권한을 막지 않는지 확인.")
    lines.append(
        "3) AWS Console → Amazon Bedrock → Model access: 해당 Claude 모델이 "
        "'Access granted'(또는 동등한 승인 상태)인지 확인."
    )
    lines.append(
        "4) inference profile ID(us./global./eu.*)가 리전 정책과 일치하는지 확인 "
        "(소스 리전이 ap-northeast-2이면 보통 global.* 프로필 사용)."
    )

    if code == "AccessDeniedException" or (
        msg and "access denied" in msg.lower()
    ):
        lines.append("")
        lines.append(
            "[이번 오류 해석] AccessDeniedException → IAM 정책/SCP/모델 액세스 중 하나에서 "
            "InvokeModel이 명시적으로 거부된 경우가 많음."
        )
    if code == "ResourceNotFoundException":
        lines.append("")
        lines.append(
            "[이번 오류 해석] ResourceNotFoundException → modelId 오타, 해당 리전 미지원, "
            "레거시 모델 미사용으로 차단, 또는 Model access 미승인일 수 있음."
        )
    if code == "ValidationException":
        lines.append("")
        lines.append(
            "[이번 오류 해석] ValidationException → modelId 형식 오류, inference profile 미사용 등."
        )

    return "\n".join(lines)
