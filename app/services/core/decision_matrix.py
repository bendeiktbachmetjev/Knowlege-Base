from typing import List, Dict


def calculate_decision_matrix(
    options: List[str],
    criteria: List[str],
    weights: List[float],
    scores: List[List[float]]
) -> Dict[str, float]:
    """
    Calculate weighted decision matrix.
    options: list of option names
    criteria: list of criteria names
    weights: list of weights for each criterion (same order)
    scores: matrix [option][criterion] with scores (same order)
    Returns dict: {option: total_score}
    """
    if not (len(criteria) == len(weights)):
        raise ValueError("Criteria and weights must have the same length.")
    if not (len(options) == len(scores)):
        raise ValueError("Each option must have a list of scores.")
    for row in scores:
        if len(row) != len(criteria):
            raise ValueError("Each score row must match number of criteria.")
    result = {}
    for i, option in enumerate(options):
        total = 0.0
        for j, weight in enumerate(weights):
            total += scores[i][j] * weight
        result[option] = total
    return result 