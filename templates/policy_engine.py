def evaluate_policy(score: int) -> str:
    """
    Map a numeric risk score to an authentication policy action.

    Returns one of:
      - "allow": login proceeds normally
      - "otp": require one-time passcode (MFA)
      - "challenge": require additional challenge (e.g. security question)
      - "block": deny login or escalate to admin
    """
    if score < 30:
        return "allow"
    elif score < 60:
        return "otp"
    elif score < 80:
        return "challenge"
    else:
        return "block"
