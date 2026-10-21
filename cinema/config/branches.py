"""The 5 VOX cinemas (branches). Every branch shows 10 movies (list of movie ids)."""

BRANCHES = {
    "VOX Riyadh Park": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "VOX Sahara Mall": [101, 103, 105, 106, 108, 111, 112, 113, 114, 115],
    "VOX Al Qasr Mall": [102, 104, 105, 107, 109, 110, 111, 112, 113, 115],
    "VOX Atyaf Mall": [101, 102, 103, 106, 108, 109, 110, 112, 114, 115],
    "VOX The Sport": [101, 104, 105, 106, 107, 108, 111, 112, 113, 114],
}


def where_showing(movie_id: int) -> list[str]:
    """Names of the branches that show this movie."""
    return [branch for branch, movie_ids in BRANCHES.items() if movie_id in movie_ids]
