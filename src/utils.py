from datetime import datetime

def parse_date(date):
    """
    Converts dates from different formats to a common format.
    Accepts the following fomats:
    - MM/YYYY (ex.: "09/2024")
    - mes/AA (ex.: "set/24")

    Args:
        date (str): String indicating the date.

    Returns:
        datetime: corresponding datetiem object.

    Raises:
        ValueError: Se the date format is unknown.
    """
    try:
        # First, try the format "MM/YYYY"
        return datetime.strptime(date, "%m/%Y")
    except ValueError:
        pass  # If it fails, try the next format
    
    try:
        # Next, try the format "mon/YY"
        months = {
            "jan": "01", "fev": "02", "mar": "03", "abr": "04", "mai": "05", "jun": "06",
            "jul": "07", "ago": "08", "set": "09", "out": "10", "nov": "11", "dez": "12"
        }
        # Extract month and year from the format "mon/YY"
        try:
            month_abbr, year = date.split("/")
        except ValueError:
            raise ValueError(f"Unknown date format: {date}")
        month_abbr_lower = month_abbr.lower()
        if month_abbr_lower not in months:
            raise ValueError(f"Unknown date format: {date}")
        month = months[month_abbr_lower]  # Convert the abbreviated month to number
        full_year = "20" + year  # Add "20" to the abbreviated year
        return datetime.strptime(f"{month}/{full_year}", "%m/%Y")
    except (ValueError, KeyError):
        raise ValueError(f"Unknown date format: {date}")

def check_cbo_description(cbo_description, terms):
    """Function to check if the "CBO DESCRIPTION" contains the desired terms"""
    cbo_description = cbo_description.upper()  # Convert to uppercase to avoid case-sensitive issues
    return all(term in cbo_description for term in terms)