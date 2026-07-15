def recommendation_ids(scores):
    """Extract item IDs from PyGorse scored recommendations."""
    return [score.id for score in scores]
