import re
from collections import Counter

class QualityScorer:
    """
    Scores Reddit content calendar quality across multiple dimensions
    """
    
    def __init__(self):
        self.weights = {
            'naturalness': 0.30,
            'persona_variety': 0.15,
            'timing_realism': 0.15,
            'content_diversity': 0.20,
            'anti_spam_score': 0.20
        }
    
    def score_calendar(self, posts, personas):
        """
        Score the entire calendar and return metrics
        """
        scores = {}
        all_warnings = []
        
        # Calculate individual scores
        naturalness, nat_warnings = self._check_naturalness(posts)
        scores['naturalness'] = naturalness
        all_warnings.extend(nat_warnings)
        
        persona_variety, pers_warnings = self._check_persona_variety(posts, personas)
        scores['persona_variety'] = persona_variety
        all_warnings.extend(pers_warnings)
        
        timing_realism, time_warnings = self._check_timing_realism(posts)
        scores['timing_realism'] = timing_realism
        all_warnings.extend(time_warnings)
        
        content_diversity, cont_warnings = self._check_content_diversity(posts)
        scores['content_diversity'] = content_diversity
        all_warnings.extend(cont_warnings)
        
        anti_spam, spam_warnings = self._check_anti_spam(posts)
        scores['anti_spam_score'] = anti_spam
        all_warnings.extend(spam_warnings)
        
        # Calculate weighted overall score
        overall = sum(scores[key] * self.weights[key] for key in scores)
        
        return {
            **scores,
            'overall_score': round(overall, 1),
            'warnings': all_warnings
        }
    
    def _check_naturalness(self, posts):
        """
        Check if posts and comments sound natural
        """
        score = 10
        issues = []
        
        # Check for unnatural phrases
        unnatural_phrases = [
            'as an ai', 'i am a bot', 'click here', 'buy now',
            'limited time', 'act now', 'special offer'
        ]
        
        all_text = []
        for post in posts:
            all_text.append(post['title'].lower())
            all_text.append(post['body'].lower())
            for comment in post['comments']:
                all_text.append(comment['comment_text'].lower())
        
        combined_text = ' '.join(all_text)
        
        for phrase in unnatural_phrases:
            if phrase in combined_text:
                score -= 2
                issues.append(f"Unnatural phrase detected: '{phrase}'")
        
        # Check for overly formal language
        if any(word in combined_text for word in ['furthermore', 'moreover', 'nevertheless', 'henceforth']):
            score -= 1
            issues.append("Language too formal for Reddit")
        
        return max(0, score), issues
    
    def _check_persona_variety(self, posts, personas):
        """
        Check if personas are used with good variety
        """
        score = 10
        issues = []
        
        # Count persona usage
        persona_counts = Counter()
        for post in posts:
            persona_counts[post['author_username']] += 1
            for comment in post['comments']:
                persona_counts[comment['username']] += 1
        
        # Check for overused personas
        total_interactions = sum(persona_counts.values())
        for persona, count in persona_counts.items():
            usage_pct = (count / total_interactions) * 100
            if usage_pct > 40:  # One persona doing more than 40%
                score -= 2
                issues.append(f"Persona '{persona}' overused ({usage_pct:.1f}% of interactions)")
        
        # Check if all personas are used
        persona_usernames = [p['username'] for p in personas]
        unused = set(persona_usernames) - set(persona_counts.keys())
        if unused:
            score -= 1
            issues.append(f"Personas not used: {', '.join(unused)}")
        
        return max(0, score), issues
    
    def _check_timing_realism(self, posts):
        """
        Check if timing patterns look realistic
        """
        score = 10
        issues = []
        
        all_delays = []
        for post in posts:
            for comment in post['comments']:
                all_delays.append(comment['delay_minutes'])
        
        if not all_delays:
            return score, issues
        
        # Check for suspiciously regular timing
        if len(set(all_delays)) < len(all_delays) * 0.7:  # Less than 70% unique
            score -= 2
            issues.append("Timing patterns too regular")
        
        # Check for unrealistic patterns (all same delay)
        if len(set(all_delays)) == 1:
            score -= 3
            issues.append("All comments have identical delay times")
        
        # Check for reasonable delay ranges
        if all_delays:
            avg_delay = sum(all_delays) / len(all_delays)
            if avg_delay < 10:  # Too fast
                score -= 1
                issues.append("Comments posted too quickly on average")
            if avg_delay > 200:  # Too slow
                score -= 1
                issues.append("Comments posted too slowly on average")
        
        return max(0, score), issues
    
    def _check_content_diversity(self, posts):
        """
        Check if content is diverse and not repetitive
        """
        score = 10
        issues = []
        
        # Check title diversity
        titles = [post['title'].lower() for post in posts]
        title_words = []
        for title in titles:
            title_words.extend(re.findall(r'\w+', title))
        
        # Check for repeated words in titles
        word_counts = Counter(title_words)
        common_words = {'the', 'a', 'an', 'for', 'to', 'in', 'on', 'of', 'and', 'or', 'how', 'what', 'best'}
        
        for word, count in word_counts.items():
            if word not in common_words and count > 2:
                score -= 0.5
                issues.append(f"Repeated words in titles: {word}")
        
        # Check keyword diversity across posts
        all_keywords = []
        for post in posts:
            all_keywords.extend(post.get('keyword_ids', []))
        
        if len(set(all_keywords)) < len(all_keywords) * 0.8:  # Less than 80% unique
            score -= 1
            issues.append("Low keyword diversity across posts")
        
        return max(0, score), issues
    
    def _check_anti_spam(self, posts):
        """
        Check for spam indicators and repetitive patterns
        """
        score = 10
        issues = []
        
        # Collect all comment text
        all_comments = []
        for post in posts:
            for comment in post['comments']:
                all_comments.append(comment['comment_text'].lower())
        
        if not all_comments:
            return score, issues
        
        # Check for promotional words
        promo_words = ['revolutionary', 'game-changer', 'best ever', 'must-have', 
                       'life-changing', 'perfect solution', 'amazing tool',
                       'check out', 'click here', 'sign up']
        promo_count = sum(1 for comment in all_comments 
                         for word in promo_words if word in comment)
        
        if promo_count > 2:
            score -= 2
            issues.append(f"Promotional language detected ({promo_count} instances)")
        
        # Check for repetitive opening phrases
        repetitive_openers = ['totally', 'i feel you', 'i totally', 'totally feel',
                             'totally get', 'i get that', "i've been using", 
                             "i've tried", "i've been trying"]
        
        opener_counts = {}
        for comment in all_comments:
            first_15_words = ' '.join(comment.split()[:15])
            for opener in repetitive_openers:
                if opener in first_15_words:
                    opener_counts[opener] = opener_counts.get(opener, 0) + 1
        
        # Flag if any opener used more than twice
        for opener, count in opener_counts.items():
            if count > 2:
                score -= 1.5
                issues.append(f"Repetitive opener '{opener}' used {count} times")
        
        # Check for "not perfect" overuse
        not_perfect_count = sum(1 for c in all_comments if 'not perfect' in c or "isn't perfect" in c)
        if not_perfect_count > len(all_comments) * 0.4:  # More than 40%
            score -= 1
            issues.append(f"Disclaimer phrase 'not perfect' overused ({not_perfect_count} times)")
        
        # Check for exclamation mark spam
        exclamation_count = sum(1 for c in all_comments if c.count('!') > 0)
        if exclamation_count > len(all_comments) * 0.7:  # More than 70%
            score -= 0.5
            issues.append(f"Exclamation marks overused ({exclamation_count}/{len(all_comments)} comments)")
        
        # Check for company mention frequency
        company_mentions = sum(1 for comment in all_comments 
                              if any(word in comment for word in ['slideforge', 'itinitrip', 'codesnap', 'thumbnailai', 'fitflow', 'outreachiq']))
        
        if company_mentions > len(posts) * 2:  # More than 2 mentions per post
            score -= 1
            issues.append(f"Company mentioned too frequently ({company_mentions} times)")
        
        # Check for similar comment lengths (lack of variety)
        comment_lengths = [len(c.split()) for c in all_comments]
        if len(comment_lengths) > 3:  # Only check if we have enough comments
            unique_lengths = len(set(comment_lengths))
            if unique_lengths < len(comment_lengths) * 0.5:  # Less than 50% unique lengths
                score -= 0.5
                issues.append("Comment lengths too similar (lack of variety)")
        
        # Check for word diversity
        all_words = ' '.join(all_comments).split()
        unique_ratio = len(set(all_words)) / len(all_words) if all_words else 1
        
        if unique_ratio < 0.5:  # Less than 50% unique words
            score -= 1
            issues.append(f"Low word diversity (unique ratio: {unique_ratio:.2f})")
        
        return max(0, score), issues