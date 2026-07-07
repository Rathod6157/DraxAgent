from difflib import SequenceMatcher
from app_utils import get_all_applications
from terminal import safe_print

APPLICATION_CACHE = None


def get_cached_applications():

    global APPLICATION_CACHE

    if APPLICATION_CACHE is None:
        safe_print("🔍 Indexing applications...")
        APPLICATION_CACHE = get_all_applications()
        safe_print(f"✅ Indexed {len(APPLICATION_CACHE)} applications.")

    return APPLICATION_CACHE

def refresh_application_cache():

    global APPLICATION_CACHE

    safe_print("🔄 Refreshing application index...")

    APPLICATION_CACHE = get_all_applications()

    safe_print(f"✅ Indexed {len(APPLICATION_CACHE)} applications.")

    return APPLICATION_CACHE

def similarity(query, candidate):

    query = query.lower().strip()
    candidate = candidate.lower().strip()

    # Exact full application name always wins
    if query == candidate:
        return 1.0

    candidate_words = candidate.split()

    # 1. Full-name similarity
    full_score = SequenceMatcher(
        None,
        query,
        candidate
    ).ratio()

    # 2. Individual-word similarity
    word_scores = [
        SequenceMatcher(None, query, word).ratio()
        for word in candidate_words
    ]

    best_word_score = max(word_scores, default=0)

    # 3. Prefix matching
    prefix_score = 0

    if any(word.startswith(query) for word in candidate_words):
        prefix_score = 0.9

    # 4. Acronym matching
    acronym = "".join(
        word[0]
        for word in candidate_words
        if word
    )

    acronym_score = SequenceMatcher(
        None,
        query,
        acronym
    ).ratio()

    return max(
        full_score,
        best_word_score,
        prefix_score,
        acronym_score
    )


def resolve_application(query, limit=5):

    if not query or not query.strip():
        return []

    applications = get_cached_applications()

    matches = []

    for app_name, app_data in applications.items():

        score = similarity(query, app_name)

        matches.append({
            "name": app_data["name"],
            "launch_target": app_data["launch_target"],
            "source": app_data["source"],
            "score": score
        })

    matches.sort(
        key=lambda match: (
            match["score"],
            -len(match["name"])
        ),
        reverse=True
    )

    return matches[:limit]

def decide_application(query):

    results = resolve_application(query)

    if not results:
        return {
            "status": "not_found",
            "query": query,
            "match": None,
            "alternatives": []
        }

    best = results[0]
    second = results[1] if len(results) > 1 else None

    best_score = best["score"]
    second_score = second["score"] if second else 0

    score_gap = best_score - second_score
    
    MINIMUM_MATCH_SCORE = 0.60

    if best_score < MINIMUM_MATCH_SCORE:
        return {
            "status": "not_found",
            "query": query,
            "match": None,
            "alternatives": []
        }

    # Very confident result
    if best_score >= 0.95:
        return {
            "status": "resolved",
            "query": query,
            "match": best,
            "alternatives": []
        }

    # Strong winner, but ask user before opening
    if best_score >= 0.70 and score_gap >= 0.10:
        return {
            "status": "confirm",
            "query": query,
            "match": best,
            "alternatives": results[1:3]
        }

    # Several plausible matches
    return {
        "status": "ambiguous",
        "query": query,
        "match": best,
        "alternatives": results[1:4]
    }

if __name__ == "__main__":

    for query in [
        "settings",
        "phot",
        "photos",
        "clock",
        "chrm"
    ]:

        decision = decide_application(query)

        print(f"\nQUERY: {query}")
        print("STATUS:", decision["status"])

        if decision["match"]:
            print(
                "MATCH:",
                decision["match"]["name"],
                round(decision["match"]["score"], 2),
                f"({decision['match']['source']})"
            )

        if decision["alternatives"]:
            print("ALTERNATIVES:")

            for alternative in decision["alternatives"]:
                print(
                    "-",
                    alternative["name"],
                    round(alternative["score"], 2),
                    f"({alternative['source']})"
                )