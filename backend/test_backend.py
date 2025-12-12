"""
Test script to verify backend functionality
"""

import os
from dotenv import load_dotenv
from algorithm import RedditCalendarGenerator

load_dotenv()

# Sample test data
SAMPLE_DATA = {
    "company_info": "SlideForge - AI-powered presentation tool that automates slide design",
    "personas": [
        {
            "username": "riley_ops",
            "info": "Operations head at a SaaS startup, detail-oriented, struggles with presentation design"
        },
        {
            "username": "jordan_consults",
            "info": "Independent consultant, values storytelling and clean visuals"
        },
        {
            "username": "emily_econ",
            "info": "Economics student, perfectionist, unofficial slide maker for group projects"
        }
    ],
    "subreddits": [
        "r/PowerPoint",
        "r/startups",
        "r/productivity"
    ],
    "keywords": [
        "best ai presentation maker",
        "pitch deck generator",
        "automate presentations"
    ],
    "posts_per_week": 3
}

def test_calendar_generation():
    """Test basic calendar generation"""
    print("🧪 Testing Reddit Calendar Generator...")
    print("=" * 60)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        return
    
    generator = RedditCalendarGenerator(api_key)
    
    try:
        print("\n📅 Generating Week 1 calendar...")
        calendar = generator.generate_calendar(
            company_info=SAMPLE_DATA['company_info'],
            personas=SAMPLE_DATA['personas'],
            subreddits=SAMPLE_DATA['subreddits'],
            keywords=SAMPLE_DATA['keywords'],
            posts_per_week=SAMPLE_DATA['posts_per_week'],
            week_number=1
        )
        
        print(f"\n✅ Successfully generated calendar!")
        print(f"📊 Quality Score: {calendar['quality_score']}/10")
        print(f"📅 Week: {calendar['week']}")
        print(f"📆 Date Range: {calendar['start_date']} to {calendar['end_date']}")
        print(f"📝 Total Posts: {len(calendar['posts'])}")
        
        print("\n📋 Quality Metrics:")
        for metric, score in calendar['metrics'].items():
            if metric != 'warnings' and metric != 'overall_score':
                print(f"  • {metric}: {score}/10")
        
        if calendar['metrics']['warnings']:
            print("\n⚠️ Warnings:")
            for warning in calendar['metrics']['warnings']:
                print(f"  • {warning}")
        
        print("\n📝 Generated Posts:")
        print("=" * 60)
        for i, post in enumerate(calendar['posts'], 1):
            print(f"\n{i}. POST {post['post_id']} - {post['subreddit']}")
            print(f"   Title: {post['title']}")
            print(f"   Author: {post['author_username']}")
            print(f"   Comments: {len(post['comments'])}")
        
        print("\n✅ TEST PASSED!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_generation()
