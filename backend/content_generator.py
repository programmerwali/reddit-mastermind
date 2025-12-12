from openai import OpenAI
import json

class ContentGenerator:
    """
    Uses OpenAI to generate natural Reddit posts and comments with high variety
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
        Generate a natural Reddit comment with high variety
        """
        
        company_name = self._extract_company_name(company_info)
        
        # Build prompt based on context
        if is_first_comment and should_mention_product:
            product_instruction = f"""You should naturally mention {company_name} as something you've used/tried, but:
- Make it casual, not promotional
- VARY how you mention it (don't always say "I've been using...")
- Sometimes be direct, sometimes add disclaimers, sometimes be skeptical
- Mix it up: "been using X", "tried X recently", "X works for this", "heard good things about X"
- DON'T always say "it's not perfect" - vary your qualifiers
- Use your persona's voice"""
        else:
            product_instruction = f"DO NOT mention {company_name}. Just be helpful and conversational."
        
        context = f"Original post: {post_content}"
        if previous_comment:
            context += f"\n\nYou're replying to: {previous_comment}"
        
        prompt = f"""You are {persona['username']}, a real Reddit user with this background:

{persona['info']}

{context}

Write a NATURAL Reddit comment with HIGH VARIETY.

CRITICAL VARIETY RULES:
- DON'T start with "Totally" or "I feel you" every time
- MIX comment lengths: some 1 sentence, some 2-3, occasionally 4
- VARY openers: "yeah", "lol same", "tbh", "ngl", "+1", "this", "honestly", "imo", "fwiw", "same here"
- NOT every comment needs "!" - mix periods, no punctuation, casual tone
- DON'T always acknowledge limitations - sometimes just recommend directly
- Use Reddit slang naturally: "ngl", "tbh", "imo", "fwiw", "tbf", "lol", "lmao"
- VARY structure - don't follow formula every time
- Some comments can be SHORT: "this", "^^", "same lol", "saved"
- Mix direct answers with personal anecdotes
- Don't be overly helpful - sometimes be brief or casual

{product_instruction}

EXAMPLES OF VARIETY (good vs bad):

❌ Bad (repetitive): "Totally feel you! I've been using Tool X. It's not perfect but helps."
✅ Good: "lol same. been using Tool X, does the job"

❌ Bad: "I totally get that struggle! Tool Y has been great. It's not perfect though."
✅ Good: "Tool Y worked for me. bit clunky at first ngl"

❌ Bad: "Totally! I've tried Tool Z. Not perfect but saves time!"
✅ Good: "honestly just use Tool Z. saved me hours"

❌ Bad: "I feel you on that! Have you tried X? It's helped me a lot!"
✅ Good: "yeah X is solid for this"

❌ Bad: "Totally get that! I've been using Y and it works great!"
✅ Good: "been there. Y fixes most of it"

Return ONLY the comment text, no JSON, no markdown."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Reddit user writing natural, varied comments. Never be formulaic or repetitive."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.1  # Increased for more variety
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