from openai import OpenAI
import json

class ContentGenerator:
    """
    Uses OpenAI to generate natural Reddit posts and comments
    """
    
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        
    def generate_post(self, subreddit, keywords, persona, company_info):
        """
        Generate a natural Reddit post
        """
        
        # Extract company name from company_info
        company_name = self._extract_company_name(company_info)
        
        prompt = f"""You are {persona['username']}, a real Reddit user with this background:

{persona['info']}

Generate a NATURAL Reddit post for {subreddit} related to these keywords: {', '.join(keywords)}.

CRITICAL RULES:
1. Write like a REAL Reddit user asking a genuine question or starting a discussion
2. Be casual, conversational, natural - use Reddit language (lol, tbh, etc when appropriate)
3. DO NOT mention {company_name} in the post - you're asking a question, not promoting
4. Keep it short (2-4 sentences max)
5. Show you've put thought into it (mention what you've tried, your situation, etc)
6. Match your persona's voice and background

BAD example: "What's the best AI tool for presentations? Looking for recommendations."
GOOD example: "Anyone else drowning in deck formatting? I spend more time fixing alignment than actually presenting lol. What's your workflow?"

Return ONLY a JSON object with this structure:
{{
    "title": "The post title (short, Reddit-style)",
    "body": "The post body (2-4 sentences)"
}}"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Reddit content expert who writes authentic, natural posts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            post_data = json.loads(content.strip())
            return post_data
        except:
            # Fallback if JSON parsing fails
            return {
                "title": f"Looking for advice on {keywords[0]}",
                "body": "Has anyone had experience with this? Would love to hear your thoughts."
            }
    
    def generate_comment(self, post_content, persona, company_info, is_first_comment, 
                        should_mention_product, previous_comment=None):
        """
        Generate a natural Reddit comment
        """
        
        company_name = self._extract_company_name(company_info)
        
        # Build prompt based on context
        if is_first_comment and should_mention_product:
            product_instruction = f"""You should naturally mention {company_name} as something you've used/tried, but:
- Make it casual, not promotional ("I've been using {company_name}..." not "Try {company_name}!")
- Acknowledge limitations ("it's not perfect but..." or "took some getting used to...")
- Be helpful first, product mention second
- Use your persona's voice"""
        else:
            product_instruction = f"DO NOT mention {company_name}. Just be helpful and conversational."
        
        context = f"Original post: {post_content}"
        if previous_comment:
            context += f"\n\nYou're replying to: {previous_comment}"
        
        prompt = f"""You are {persona['username']}, a real Reddit user with this background:

{persona['info']}

{context}

Write a NATURAL Reddit comment. 

RULES:
1. Write like a REAL Reddit user - casual, helpful, conversational
2. Keep it SHORT (1-3 sentences, occasionally 4)
3. Use Reddit language naturally (lol, tbh, +1, etc when appropriate)
4. {product_instruction}
5. Show personality from your background
6. If replying to a comment, acknowledge what they said

BAD: "I recommend SlideForge. It's a great tool with many features including..."
GOOD: "I've tried a bunch of tools. Slideforge is the only one that doesn't make me fight the layout. Still fix things after, but it's a decent starting point."

Return ONLY the comment text, no JSON, no markdown."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Reddit user writing natural, helpful comments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )
        
        comment = response.choices[0].message.content.strip()
        
        # Clean up any markdown or quotes
        comment = comment.strip('"').strip("'")
        
        return comment
    
    def _extract_company_name(self, company_info):
        """
        Extract company name from company info string
        """
        # Try to get the first word/phrase before a dash or comma
        if '-' in company_info:
            return company_info.split('-')[0].strip()
        elif ',' in company_info:
            return company_info.split(',')[0].strip()
        else:
            # Take first few words
            words = company_info.split()
            return ' '.join(words[:2]) if len(words) > 1 else words[0]
