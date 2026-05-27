from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_matches(user_profile, scholarships):

    texts = []

    for s in scholarships:
        text = f"{s.title} {s.eligibility} {s.description} {s.country} {s.degree_level}"
        texts.append(text)

    # combine user + scholarships
    documents = [user_profile] + texts

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    results = []

    for i, score in enumerate(similarity_scores):
        results.append({
            "scholarship_index": i,
            "score": float(score)
        })

    # sort best matches first
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results