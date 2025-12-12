import re
from collections import Counter

class QualityScorer:
    """
    Evaluates the quality of generated content calendars
    Scores from 1-10 on various metrics
    """
    
    def __init__(self):
        # Red flags for promotional content
        self.promotional_words = [
            'revolutionary', 'game-changer', 'amazing', 'incredible', 
            'transform', 'must-have', 'best solution', 'perfect for',
            'highly recommend', 'you should definitely', 'try this',
            'check out', 'visit', 'sign up'
        ]
        
    def score_calendar(self, posts, personas):
        """
        Score the entire calendar across multiple dimensions
        """
        
        warnings = []
        
        # 1. Naturalness: How authentic do posts/comments feel?
        naturalness = self._score_naturalness(posts, warnings)
        
        # 2. Persona Variety: Are personas used evenly?
        persona_variety = self._score_persona_variety(posts, personas, warnings)
        
        # 3. Timing Realism: Do delays seem organic?
        timing_realism = self._score_timing(posts, warnings)
        
        # 4. Content Diversity: Are topics varied?
        content_diversity = self._score_content_diversity(posts, warnings)
        
        # 5. Anti-Spam: Does it pass the "not spam" test?
        anti_spam = self._score_anti_spam(posts, warnings)
        
        # Calculate overall score (weighted average)
        overall = (
            naturalness * 0.3 +
            persona_variety * 0.15 +
            timing_realism * 0.15 +
            content_diversity * 0.2 +
            anti_spam * 0.2
        )
        
        return {
            "overall_score": round(overall, 1),
            "naturalness": naturalness,
            "persona_variety": persona_variety,
            "timing_realism": timing_realism,
            "content_diversity": content_diversity,
            "anti_spam_score": anti_spam,
            "warnings": warnings
        }
    
    def _score_naturalness(self, posts, warnings):
        """Score how natural the content feels (1-10)"""
        score = 10.0
        
        for post in posts:
            # Check post length
            post_length = len(post['body'].split())
            if post_length < 5:
                score -= 0.5
                warnings.append(f"Post {post['post_id']} is very short")
            elif post_length > 100:
                score -= 0.5
                warnings.append(f"Post {post['post_id']} is very long")
            
            # Check for promotional language
            promo_count = self._count_promotional_words(post['body'])
            if promo_count > 0:
                score -= promo_count * 0.5
                warnings.append(f"Post {post['post_id']} contains promotional language")
            
            # Check comments
            for comment in post['comments']:
                comment_length = len(comment['comment_text'].split())
                if comment_length > 80:
                    score -= 0.3
                    warnings.append(f"Comment {comment['comment_id']} is too long")
                
                promo_count = self._count_promotional_words(comment['comment_text'])
                if promo_count > 2:
                    score -= 0.5
                    warnings.append(f"Comment {comment['comment_id']} is too promotional")
        
        return max(1, min(10, score))
    
    def _score_persona_variety(self, posts, personas, warnings):
        """Score how evenly personas are distributed (1-10)"""
        score = 10.0
        
        # Count persona usage
        persona_usage = Counter()
        for post in posts:
            persona_usage[post['author_username']] += 1
            for comment in post['comments']:
                persona_usage[comment['username']] += 1
        
        # Check if any persona is overused
        total_actions = sum(persona_usage.values())
        for persona_name, count in persona_usage.items():
            usage_pct = count / total_actions
            if usage_pct > 0.5:
                score -= 3
                warnings.append(f"Persona {persona_name} is overused ({usage_pct*100:.1f}%)")
            elif usage_pct > 0.4:
                score -= 1
                warnings.append(f"Persona {persona_name} is heavily used ({usage_pct*100:.1f}%)")
        
        # Check if any persona is completely unused
        all_usernames = {p['username'] for p in personas}
        used_usernames = set(persona_usage.keys())
        unused = all_usernames - used_usernames
        
        if unused:
            score -= len(unused) * 0.5
            warnings.append(f"Personas not used: {', '.join(unused)}")
        
        return max(1, min(10, score))
    
    def _score_timing(self, posts, warnings):
        """Score how realistic the timing delays are (1-10)"""
        score = 10.0
        
        for post in posts:
            delays = [c['delay_minutes'] for c in post['comments']]
            
            # Too many instant replies is suspicious
            quick_replies = sum(1 for d in delays if d < 10)
            if quick_replies > len(delays) * 0.5:
                score -= 2
                warnings.append(f"Post {post['post_id']}: Too many quick replies")
            
            # All replies at exact same interval is suspicious
            if len(set(delays)) == 1 and len(delays) > 1:
                score -= 3
                warnings.append(f"Post {post['post_id']}: All replies have same delay")
        
        return max(1, min(10, score))
    
    def _score_content_diversity(self, posts, warnings):
        """Score how varied the content is (1-10)"""
        score = 10.0
        
        # Check title similarity
        titles = [post['title'].lower() for post in posts]
        all_words = ' '.join(titles).split()
        word_freq = Counter(all_words)
        
        # If too many repeated words, content might be repetitive
        repeated_words = [word for word, count in word_freq.items() 
                         if count > len(posts) * 0.6 and len(word) > 4]
        
        if repeated_words:
            score -= len(repeated_words) * 0.5
            warnings.append(f"Repeated words in titles: {', '.join(repeated_words)}")
        
        # Check if posts are in same subreddit
        subreddits = [post['subreddit'] for post in posts]
        subreddit_counts = Counter(subreddits)
        
        for sub, count in subreddit_counts.items():
            if count > 2:
                score -= 2
                warnings.append(f"Too many posts in {sub} ({count} posts)")
        
        return max(1, min(10, score))
    
    def _score_anti_spam(self, posts, warnings):
        """Score how well content avoids spam patterns (1-10)"""
        score = 10.0
        
        # Check company mentions frequency
        company_mentions = 0
        for post in posts:
            for comment in post['comments']:
                words = comment['comment_text'].split()
                capital_words = [w for w in words if w and w[0].isupper() and len(w) > 3]
                if capital_words:
                    company_mentions += 1
        
        # Too many mentions is spammy
        if company_mentions > len(posts) * 1.5:
            score -= 2
            warnings.append(f"Company mentioned too frequently ({company_mentions} times)")
        
        # Check for identical phrasing across posts
        all_comments = []
        for post in posts:
            for comment in post['comments']:
                all_comments.append(comment['comment_text'].lower())
        
        # Look for repeated phrases
        for i, comment1 in enumerate(all_comments):
            for comment2 in all_comments[i+1:]:
                similarity = self._similarity_score(comment1, comment2)
                if similarity > 0.7:
                    score -= 1
                    warnings.append("Very similar comments detected")
                    break
        
        return max(1, min(10, score))
    
    def _count_promotional_words(self, text):
        """Count promotional/marketing words in text"""
        text_lower = text.lower()
        count = sum(1 for word in self.promotional_words if word in text_lower)
        return count
    
    def _similarity_score(self, text1, text2):
        """Calculate similarity between two texts (0-1)"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
