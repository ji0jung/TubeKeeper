from uuid import UUID


def extract_user_id_from_token(token: str) -> UUID:
    """JWT 토큰에서 사용자 ID 추출 (간단한 구현)"""
    # 현재는 토큰 형식이 "jwt_token_for_{user_id}" 이므로 파싱
    if token.startswith("jwt_token_for_"):
        user_id_str = token.replace("jwt_token_for_", "")
        return UUID(user_id_str)
    
    raise ValueError("Invalid token format")
