def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate BMI given weight in kilograms and height in centimeters.
    Returns BMI rounded to 2 decimals.
    Raises ValueError for invalid input.
    """
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive numbers.")
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)
