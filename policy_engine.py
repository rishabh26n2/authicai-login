def evaluate_policy(score: int) -> str:
    """
    Returns one of:
    - 'allow'
    - 'challenge' (security question)
    - 'otp'
    - 'otp_email'
    - 'block'
    """
    if score < 20:
        return "allow"
    elif score < 40:
        return "challenge"
    elif score < 70:
        return "otp"
    elif score < 85:
        return "otp_email"
    else:
        return "block"
