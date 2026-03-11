def detect_attack(features):

    # Data Exfiltration Detection
    if features["file_size"] > 500000:
        return True, "Data Exfiltration Attack", "High"

    # Brute Force Login Detection
    if features["failed_attempts"] >= 3:
        return True, "Brute-Force Login Attack", "Medium"

    return False, "Normal Activity", "Low"
