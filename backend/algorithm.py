import random
import json
from datetime import datetime, timedelta
from content_generator import ContentGenerator
from quality_scorer import QualityScorer

class RedditCalendarGenerator:
    """
    Core algorithm for generating Reddit content calendars
    """
    
    def __init__(self, api_key):
        self.content_gen = ContentGenerator(api_key)
        self.quality_scorer = QualityScorer()
        
    def generate_calendar(self, company_info, personas, subreddits, keywords, 
                         posts_per_week, week_number=1, previous_calendar=None):
        """
        Generate a complete content calendar for a week
        """
        
        # Calculate week dates
        start_date = datetime.now() + timedelta(days=7 * (week_number - 1))
        end_date = start_date + timedelta(days=6)
        
        # Step 1: Select topics and subreddits for posts
        post_assignments = self._assign_posts_to_subreddits(
            subreddits, keywords, posts_per_week, previous_calendar
        )
        
        # Step 2: Generate posts with comments
        posts = []
        for i, assignment in enumerate(post_assignments):
            post = self._generate_post_with_comments(
                assignment=assignment,
                personas=personas,
                company_info=company_info,
                post_number=i + 1,
                start_date=start_date,
                week_number=week_number
            )
            posts.append(post)
        
        # Step 3: Score quality
        quality_metrics = self.quality_scorer.score_calendar(posts, personas)
        
        calendar = {
            "week": week_number,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "posts": posts,
            "quality_score": quality_metrics['overall_score'],
            "metrics": quality_metrics
        }
        
        return calendar
    
    def _assign_posts_to_subreddits(self, subreddits, keywords, posts_per_week, previous_calendar):
        """
        Intelligently assign posts to subreddits
        """
        
        # Track recent topics if we have previous calendar
        used_keywords = set()
        if previous_calendar and 'posts' in previous_calendar:
            for post in previous_calendar['posts']:
                used_keywords.update(post.get('keyword_ids', []))
        
        # Filter out recently used keywords
        available_keywords = [k for k in keywords if k not in used_keywords or random.random() > 0.7]
        if len(available_keywords) < posts_per_week:
            available_keywords = keywords
        
        # Shuffle for variety
        random.shuffle(available_keywords)
        random.shuffle(subreddits)
        
        assignments = []
        subreddit_usage = {sub: 0 for sub in subreddits}
        
        for i in range(posts_per_week):
            # Select keyword
            keyword = available_keywords[i % len(available_keywords)]
            
            # Select subreddit (prefer those used less)
            available_subs = [s for s, count in subreddit_usage.items() if count < 2]
            if not available_subs:
                available_subs = subreddits
            
            subreddit = random.choice(available_subs)
            subreddit_usage[subreddit] += 1
            
            assignments.append({
                'subreddit': subreddit,
                'keywords': [keyword],
                'post_index': i
            })
        
        return assignments
    
    def _generate_post_with_comments(self, assignment, personas, company_info, 
                                    post_number, start_date, week_number):
        """
        Generate a single post with its comment thread
        """
        
        # Distribute posts across the week
        days_offset = [0, 2, 4, 6, 1, 3, 5]
        day_offset = days_offset[post_number % len(days_offset)]
        
        post_time = start_date + timedelta(
            days=day_offset,
            hours=random.randint(9, 18),
            minutes=random.randint(0, 59)
        )
        
        # Select personas for this thread
        primary_persona = random.choice(personas)
        
        # Secondary personas (reply)
        other_personas = [p for p in personas if p['username'] != primary_persona['username']]
        num_commenters = min(random.randint(2, 4), len(other_personas))
        commenting_personas = random.sample(other_personas, num_commenters)
        
        # Generate post content
        post_data = self.content_gen.generate_post(
            subreddit=assignment['subreddit'],
            keywords=assignment['keywords'],
            persona=primary_persona,
            company_info=company_info
        )
        
        # Generate post ID
        post_id = f"P{week_number}{post_number}"
        
        # Generate comments with realistic timing
        comments = self._generate_comment_thread(
            post_id=post_id,
            post_content=post_data['body'],
            commenting_personas=commenting_personas,
            company_info=company_info,
            post_time=post_time,
            week_number=week_number,
            post_number=post_number
        )
        
        post = {
            "post_id": post_id,
            "subreddit": assignment['subreddit'],
            "title": post_data['title'],
            "body": post_data['body'],
            "author_username": primary_persona['username'],
            "timestamp": post_time.strftime("%Y-%m-%d %H:%M"),
            "keyword_ids": assignment['keywords'],
            "comments": comments
        }
        
        return post
    
    def _generate_comment_thread(self, post_id, post_content, commenting_personas, 
                                 company_info, post_time, week_number, post_number):
        """
        Generate a natural comment thread with nested replies
        """
        
        comments = []
        current_time = post_time
        
        # First comment: Natural response, may mention company
        first_commenter = commenting_personas[0]
        delay_minutes = random.randint(15, 90)
        current_time += timedelta(minutes=delay_minutes)
        
        first_comment = self.content_gen.generate_comment(
            post_content=post_content,
            persona=first_commenter,
            company_info=company_info,
            is_first_comment=True,
            should_mention_product=random.random() > 0.4  # 60% chance to mention
        )
        
        comment_id = f"C{week_number}{post_number}1"
        comments.append({
            "comment_id": comment_id,
            "post_id": post_id,
            "parent_comment_id": None,
            "comment_text": first_comment,
            "username": first_commenter['username'],
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M"),
            "delay_minutes": delay_minutes
        })
        
        # Additional comments: Build on the conversation
        parent_comment_id = comment_id
        
        for i, persona in enumerate(commenting_personas[1:], start=2):
            delay_minutes = random.randint(10, 120)
            current_time += timedelta(minutes=delay_minutes)
            
            # Decide if this is a reply or new top-level comment
            is_reply = random.random() > 0.3  # 70% chance it's a reply
            
            comment = self.content_gen.generate_comment(
                post_content=post_content,
                persona=persona,
                company_info=company_info,
                is_first_comment=False,
                should_mention_product=False,
                previous_comment=comments[-1]['comment_text'] if is_reply else None
            )
            
            comment_id = f"C{week_number}{post_number}{i}"
            comments.append({
                "comment_id": comment_id,
                "post_id": post_id,
                "parent_comment_id": parent_comment_id if is_reply else None,
                "comment_text": comment,
                "username": persona['username'],
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M"),
                "delay_minutes": delay_minutes
            })
            
            # Sometimes update parent for nested threads
            if is_reply and random.random() > 0.5:
                parent_comment_id = comment_id
        
        return comments
