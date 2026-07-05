"""
Simple Online Calculator Web Application
"""

from flask import Flask, render_template, request, jsonify
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Flask app initialized")

# Routes
@app.route('/')
def index():
    """Main page with calculator interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return f"<h1>Calculator App</h1><p>Error: {str(e)}</p>", 500

@app.route('/health')
def health():
    """Health check endpoint for Elastic Beanstalk"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Calculate endpoint"""
    try:
        data = request.get_json()
        expression = data.get('expression', '')

        # Simple eval (in production, use safer expression parser)
        result = eval(expression)

        return jsonify({
            'expression': expression,
            'result': result,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/history', methods=['GET'])
def history():
    """Get calculation history"""
    return jsonify({
        'history': [],
        'message': 'Database not initialized'
    }), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
