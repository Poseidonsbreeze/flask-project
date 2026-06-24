from typing import List, Dict, Optional
from app.models import Scholarship


class ProfileTextGenerator:
    """Generates optimal profile text for better scholarship matching."""

    def __init__(self, user_field_scores: Dict[str, float], preferred_country: str = None):
        """
        Initialize the profile text generator.

        Args:
            user_field_scores: Dictionary of field preferences with scores (0-1)
            preferred_country: User's preferred country for study
        """
        self.user_field_scores = user_field_scores
        self.preferred_country = preferred_country

    def generate_optimal_text(self) -> str:
        """
        Generate optimal profile text based on user's field preferences.

        Returns:
            str: Generated profile text
        """
        text_parts = []

        if self.user_field_scores:
            field_order = sorted(self.user_field_scores.items(), key=lambda x: x[1], reverse=True)

            for field, score in field_order[:3]:
                text_parts.extend(self._get_field_description(field, score))

        if self.preferred_country:
            text_parts.append(f"Based in {self.preferred_country}, ")

        text_parts.append("seeking suitable academic opportunities and funding support.")

        return ' '.join(text_parts)

    def _get_field_description(self, field: str, score: float) -> List[str]:
        """
        Get text description for a specific field based on its score.

        Args:
            field: Field name
            score: Preference score (0-1)

        Returns:
            List[str]: List of text fragments for the field
        """
        base_descriptions = {
            'computer_science': {
                'high': 'I have a strong background in computer science, specializing in software development and algorithmic problem solving.',
                'medium': 'I possess solid computer science skills with practical programming experience.',
                'low': 'I have basic computer science knowledge and familiarity with programming concepts.',
            },
            'data_science': {
                'high': 'I am deeply interested in data science, machine learning, and statistical analysis.',
                'medium': 'I have experience with data analysis and machine learning concepts.',
                'low': 'I have some exposure to data science and analytics.',
            },
            'engineering': {
                'high': 'I excel in engineering disciplines, focusing on practical applications and design.',
                'medium': 'I have a solid foundation in engineering principles and practices.',
                'low': 'I have basic engineering knowledge and skills.',
            },
            'business': {
                'high': 'I have a keen interest in business administration and entrepreneurship.',
                'medium': 'I possess fundamental business knowledge and management skills.',
                'low': 'I have some exposure to business studies.',
            },
            'arts': {
                'high': 'I have a passion for creative arts and interdisciplinary studies.',
                'medium': 'I engage in artistic pursuits and creative expression.',
                'low': 'I have basic artistic interests and skills.',
            },
            'sciences': {
                'high': 'I am deeply interested in scientific research and laboratory work.',
                'medium': 'I have experience with scientific methods and research.',
                'low': 'I have basic scientific knowledge.',
            },
        }

        level = 'high' if score >= 0.7 else 'medium' if score >= 0.4 else 'low'

        description = base_descriptions.get(field, {}).get(level, f"I have experience in {field.replace('_', ' ')}.")

        return [
            f"with strong {self._normalize_field(field)} background, ",
            description,
            "seeking relevant opportunities."
        ]

    def _normalize_field(self, field: str) -> str:
        """Normalize field name for better text generation."""
        field_map = {
            'computer_science': 'computer science',
            'data_science': 'data science',
            'engineering': 'engineering',
            'business': 'business',
            'arts': 'arts and humanities',
            'sciences': 'sciences',
        }
        return field_map.get(field, field.replace('_', ' '))


class DeadlineAnalyzer:
    """Analyzes user profiles and suggests optimal deadline ranges for applications."""

    def __init__(self, profile_text: str):
        self.profile_text = profile_text.lower()

    def analyze_field_preference(self) -> Dict[str, float]:
        """
        Analyze user's field preferences from profile text.

        Args:
            profile_text: User's profile text

        Returns:
            Dict[str, float]: Field preferences with scores (0-1)
        """
        field_keywords = {
            'computer_science': ['computer science', 'software', 'programming', 'algorithm', 'data science', 'machine learning', 'coding', 'development'],
            'data_science': ['data science', 'analysis', 'statistics', 'machine learning', 'AI', 'big data'],
            'engineering': ['engineering', 'design', 'technical', 'practical', 'research'],
            'business': ['business', 'management', 'finance', 'entrepreneurship', 'commerce'],
            'arts': ['arts', 'creative', 'design', 'humanities', 'culture'],
            'sciences': ['science', 'research', 'laboratory', 'experimental', 'theoretical'],
        }

        scores = {}
        for field, keywords in field_keywords.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in self.profile_text)
            score = min(keyword_matches / 2, 1.0)
            scores[field] = score

        return scores


class ProfileRecommendationEngine:
    """Recommends optimal profile text based on available scholarships."""

    @staticmethod
    def get_suggested_field_descriptions() -> Dict[str, List[str]]:
        """
        Get suggested field descriptions for different academic areas.

        Returns:
            Dict[str, List[str]]: Suggested descriptions per field
        """
        return {
            'computer_science': [
                "Computer science enthusiast with programming and software development skills",
                "Technical professional with expertise in algorithms and data structures",
                "Software engineering graduate seeking opportunities in tech industry",
            ],
            'data_science': [
                "Data science specialist with machine learning and statistical analysis background",
                "Analytics professional with expertise in data visualization and predictive modeling",
                "Research-oriented data scientist interested in big data applications",
            ],
            'engineering': [
                "Engineering graduate with focus on design and implementation",
                "Technical specialist with practical problem-solving skills",
                "Applied research professional with industry experience",
            ],
            'business': [
                "Business administration graduate with entrepreneurial mindset",
                "Management professional with strategic thinking abilities",
                "Finance and economics specialist seeking business opportunities",
            ],
            'arts': [
                "Creative arts professional with interdisciplinary approach",
                "Design and media specialist with visual communication skills",
                "Cultural studies graduate interested in creative industries",
            ],
            'sciences': [
                "Research scientist with laboratory and analytical experience",
                "Scientific researcher with publications and presentations",
                "Academic scholar with strong theoretical and practical foundation",
            ],
        }

    @staticmethod
    def update_profile_text(user_id: int, new_text: str, field_scores: Dict[str, float]) -> None:
        """
        Update user's profile text and store field preferences.

        Args:
            user_id: User ID
            new_text: New profile text
            field_scores: Field preferences
        """
        from app.extensions import db
        from app.models import User

        user = User.query.get(user_id)
        if user:
            user.profile_text = new_text
            db.session.commit()


class ProfileTextValidator:
    """Validates and optimizes profile text for better matching."""

    @staticmethod
    def validate_text_quality(text: str) -> Dict[str, any]:
        """
        Validate profile text quality and provide suggestions.

        Args:
            text: Profile text to validate

        Returns:
            Dict[str, any]: Validation results with suggestions
        """
        results = {
            'length': len(text),
            'word_count': len(text.split()),
            'has_education_keywords': False,
            'has_experience_keywords': False,
            'has_goals_keywords': False,
            'score': 0,
            'suggestions': [],
        }

        education_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'graduated', 'studied']
        experience_keywords = ['experience', 'worked', ' intern', 'project', 'skill', 'ability', 'trained']
        goals_keywords = ['seek', 'looking', 'want', 'interest', 'aspire', 'goal', 'future', 'plan']

        text_lower = text.lower()
        results['has_education_keywords'] = any(keyword in text_lower for keyword in education_keywords)
        results['has_experience_keywords'] = any(keyword in text_lower for keyword in experience_keywords)
        results['has_goals_keywords'] = any(keyword in text_lower for keyword in goals_keywords)

        if results['length'] < 50:
            results['suggestions'].append('Add more details about your background and achievements')
        elif results['length'] > 500:
            results['suggestions'].append('Consider condensing your profile to key points')

        if not results['has_education_keywords']:
            results['suggestions'].append('Include information about your education background')

        if not results['has_experience_keywords']:
            results['suggestions'].append('Add details about your work or research experience')

        if not results['has_goals_keywords']:
            results['suggestions'].append('State your career goals or interests clearly')

        score = 0
        score += 0.2 if results['has_education_keywords'] else 0
        score += 0.2 if results['has_experience_keywords'] else 0
        score += 0.2 if results['has_goals_keywords'] else 0

        if results['length'] >= 100 and results['length'] <= 300:
            score += 0.4

        results['score'] = score

        return results

    @staticmethod
    def optimize_text_for_matching(text: str) -> str:
        """
        Optimize profile text for better matching.

        Args:
            text: Original profile text

        Returns:
            str: Optimized profile text
        """
        text = text.strip()

        if len(text) < 50:
            return text + ' I am actively seeking academic and professional development opportunities.'
        elif len(text) > 500:
            sentences = text.split('. ')
            return '. '.join(sentences[:5]) + '.'

        return text


# Helper function for easy access
def generate_profile_from_scholarships(scholarships: List[Scholarship]) -> str:
    """
    Generate a profile text based on the user's scholarship interests.

    Args:
        scholarships: List of scholarships the user is interested in

    Returns:
        str: Generated profile text
    """
    field_scores = {}
    for s in scholarships:
        field = ProfileRecommendationEngine._extract_field_from_title(s.title)
        field_scores[field] = field_scores.get(field, 0) + 1

    if field_scores:
        max_score = max(field_scores.values())
        normalized_scores = {k: v/max_score for k, v in field_scores.items()}

        generator = ProfileTextGenerator(
            user_field_scores=normalized_scores,
            preferred_country=ProfileRecommendationEngine._extract_country_from_scholarships(scholarships)
        )

        return generator.generate_optimal_text()

    return "I am seeking suitable academic and professional opportunities."


@staticmethod
    def _extract_field_from_title(title: str) -> str:
        """Extract field from scholarship title."""
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in ['computer', 'software', 'coding', 'programming', 'tech']):
            return 'computer_science'
        elif any(keyword in title_lower for keyword in ['data', 'analysis', 'statistical', 'machine learning']):
            return 'data_science'
        elif any(keyword in title_lower for keyword in ['engineer', 'engineering', 'technical', 'design']):
            return 'engineering'
        elif any(keyword in title_lower for keyword in ['business', 'finance', 'management', 'commerce']):
            return 'business'
        elif any(keyword in title_lower for keyword in ['art', 'creative', 'design', 'media', 'visual']):
            return 'arts'
        elif any(keyword in title_lower for keyword in ['science', 'research', 'laboratory', 'scientific']):
            return 'sciences'
        return 'other'

    @staticmethod
    def _extract_country_from_scholarships(scholarships: List[Scholarship]) -> str:
        """Extract most common country from scholarships."""
        countries = {}
        for s in scholarships:
            if s.country:
                countries[s.country] = countries.get(s.country, 0) + 1

        if countries:
            return max(countries.items(), key=lambda x: x[1])[0]
        return None
