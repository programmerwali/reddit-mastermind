from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from algorithm import RedditCalendarGenerator
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the calendar generator
generator = RedditCalendarGenerator(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/generate-calendar', methods=['POST'])
def generate_calendar():
    """Generate initial content calendar"""
    try:
        data = request.json
        
        # Validate input
        required_fields = ['company_info', 'personas', 'subreddits', 'keywords', 'posts_per_week']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate personas (at least 2)
        if len(data['personas']) < 2:
            return jsonify({"error": "At least 2 personas required"}), 400
        
        # Generate calendar
        calendar = generator.generate_calendar(
            company_info=data['company_info'],
            personas=data['personas'],
            subreddits=data['subreddits'],
            keywords=data['keywords'],
            posts_per_week=data['posts_per_week'],
            week_number=1
        )
        
        return jsonify(calendar)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-next-week', methods=['POST'])
def generate_next_week():
    """Generate content calendar for subsequent weeks"""
    try:
        data = request.json
        
        # Validate input
        required_fields = ['company_info', 'personas', 'subreddits', 'keywords', 'posts_per_week', 'week_number']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Generate next week
        calendar = generator.generate_calendar(
            company_info=data['company_info'],
            personas=data['personas'],
            subreddits=data['subreddits'],
            keywords=data['keywords'],
            posts_per_week=data['posts_per_week'],
            week_number=data['week_number'],
            previous_calendar=data.get('previous_calendar')
        )
        
        return jsonify(calendar)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
