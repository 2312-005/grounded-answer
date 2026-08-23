from datetime import date


AMENDMENT_EFFECTIVE_DATE = date(2026, 3, 1)


def amendment_applies_to_determination(
    determination_date: date,
) -> bool:
    """
    Paragraphs 1, 3, and 4 apply to determinations
    made on or after 1 March 2026.
    """
    return determination_date >= AMENDMENT_EFFECTIVE_DATE


def reporting_amendment_applies(
    change_date: date,
) -> bool:
    """
    Paragraph 2 applies only to changes of circumstances
    occurring on or after 1 March 2026.
    """
    return change_date >= AMENDMENT_EFFECTIVE_DATE


def get_effective_earnings_disregard(
    determination_date: date,
) -> int:
    """Return the applicable monthly earnings disregard."""
    if amendment_applies_to_determination(determination_date):
        return 175

    return 120


def get_effective_sanction_percentage(
    determination_date: date,
) -> int:
    """Return the applicable sanction percentage."""
    if amendment_applies_to_determination(determination_date):
        return 15

    return 20


def get_reporting_period_days(
    change_date: date,
) -> int:
    """Return the applicable reporting period."""
    if reporting_amendment_applies(change_date):
        return 14

    return 10


def get_policy_context(
    determination_date: date,
) -> dict:
    """
    Return the date-dependent policy context that the
    answer layer can use alongside retrieved clauses.
    """
    return {
        "determination_date": determination_date.isoformat(),
        "amendment_effective_date": (
            AMENDMENT_EFFECTIVE_DATE.isoformat()
        ),
        "earnings_disregard": get_effective_earnings_disregard(
            determination_date
        ),
        "sanction_percentage": get_effective_sanction_percentage(
            determination_date
        ),
    }