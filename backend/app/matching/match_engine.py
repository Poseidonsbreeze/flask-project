from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_matches(user_profile, scholarships):

    if not scholarships:
        return []

    # ensure user_profile is a string
    user_profile = user_profile or ""

    texts = []

    for s in scholarships:
        # Safely coerce possibly None fields to empty strings
        title = s.title or ""
        eligibility = s.eligibility or ""
        description = s.description or ""
        country = s.country or ""
        degree_level = s.degree_level or ""

        text = f"{title} {eligibility} {description} {country} {degree_level}"
        texts.append(text)

    # combine user + scholarships
    documents = [user_profile] + texts

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError:
        # in case all documents are empty, return zero scores
        results = []
        for i in range(len(scholarships)):
            results.append({"scholarship_index": i, "score": 0.0})
        return results

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    # replace NaN with 0.0 to avoid sending NaN to client
    similarity_scores = np.nan_to_num(similarity_scores, nan=0.0, posinf=0.0, neginf=0.0)

    results = []

    for i, score in enumerate(similarity_scores):
        results.append({
            "scholarship_index": i,
            "score": float(score)
        })

    # sort best matches first
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results