COMPATIBILITY_MAP: dict[str, set[str]] = {
    "O-": {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"},
    "O+": {"O+", "A+", "B+", "AB+"},
    "A-": {"A-", "A+", "AB-", "AB+"},
    "A+": {"A+", "AB+"},
    "B-": {"B-", "B+", "AB-", "AB+"},
    "B+": {"B+", "AB+"},
    "AB-": {"AB-", "AB+"},
    "AB+": {"AB+"},
}


ALL_BLOOD_GROUPS = list(COMPATIBILITY_MAP.keys())


def is_compatible(donor_blood_group: str, recipient_blood_group: str) -> bool:
    return recipient_blood_group in COMPATIBILITY_MAP.get(donor_blood_group, set())


def compatibility_strength(donor_blood_group: str, recipient_blood_group: str) -> float:
    if donor_blood_group == recipient_blood_group:
        return 1.0

    if is_compatible(donor_blood_group, recipient_blood_group):
        # Slightly reward exact Rh before generic universal fit
        if donor_blood_group.endswith("-") and recipient_blood_group.endswith("-"):
            return 0.9
        return 0.8

    return 0.0
