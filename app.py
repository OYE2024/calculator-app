"""
Simple Online Calculator Web Application
Saves calculation history to PostgreSQL database
"""

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
db_user = os.environ.get('RDS_USERNAME', 'dbadmin')
db_password = os.environ.get('RDS_PASSWORD', 'password')
db_host = os.environ.get('RDS_HOSTNAME', 'localhost')
db_port = os.environ.get('RDS_PORT', '5432')
db_name = os.environ.get('RDS_DB_NAME', 'calculator_db')

# Build database URL
try:
    database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'connect_timeout': 5,
        },
        'pool_size': 5,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    logger.info(f"Database URL configured: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
except Exception as e:
    logger.error(f"Error configuring database URL: {str(e)}")

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class Calculation(db.Model):
    """Model for storing calculation history"""
    __tablename__ = 'calculations'

    id = db.Column(db.Integer, primary_key=True)
    expression = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_ip = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'expression': self.expression,
            'result': self.result,
            'timestamp': self.timestamp.isoformat(),
            'user_ip': self.user_ip
        }

# Initialize database
def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.warning(f"Database initialization warning: {str(e)}")

# Try to initialize database on startup
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")

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
    """Calculate endpoint - saves results to database"""
    try:
        data = request.get_json()
        expression = data.get('expression', '')

        if not expression:
            return jsonify({
                'success': False,
                'error': 'Expression is required'
            }), 400

        # Evaluate expression (in production, use safer expression parser)
        try:
            result = eval(expression)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid expression: {str(e)}'
            }), 400

        # Get user IP
        user_ip = request.remote_addr

        # Try to save to database
        try:
            calculation = Calculation(
                expression=expression,
                result=float(result),
                user_ip=user_ip
            )
            db.session.add(calculation)
            db.session.commit()
            logger.info(f"Calculation saved: {expression} = {result}")

            return jsonify({
                'expression': expression,
                'result': result,
                'success': True,
                'saved': True,
                'id': calculation.id
            }), 200
        except Exception as db_error:
            logger.warning(f"Failed to save to database: {str(db_error)}")
            # Still return success even if DB save fails
            return jsonify({
                'expression': expression,
                'result': result,
                'success': True,
                'saved': False,
                'message': 'Result calculated but not saved (database unavailable)'
            }), 200

    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/history', methods=['GET'])
def history():
    """Get calculation history from database"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Max 100 results

        # Try to get from database
        try:
            calculations = Calculation.query.order_by(
                Calculation.timestamp.desc()
            ).limit(limit).all()

            return jsonify({
                'success': True,
                'history': [calc.to_dict() for calc in calculations],
                'count': len(calculations)
            }), 200
        except Exception as db_error:
            logger.warning(f"Failed to retrieve history from database: {str(db_error)}")
            # Return empty history if DB is unavailable
            return jsonify({
                'success': False,
                'history': [],
                'count': 0,
                'message': 'History unavailable (database connection failed)'
            }), 200

    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/history/<int:calculation_id>', methods=['GET'])
def get_calculation(calculation_id):
    """Get specific calculation"""
    try:
        calculation = Calculation.query.get(calculation_id)

        if not calculation:
            return jsonify({
                'success': False,
                'error': 'Calculation not found'
            }), 404

        return jsonify({
            'success': True,
            'calculation': calculation.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving calculation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear calculation history"""
    try:
        try:
            count = Calculation.query.delete()
            db.session.commit()
            logger.info(f"Cleared {count} calculations from history")

            return jsonify({
                'success': True,
                'message': f'Cleared {count} calculations',
                'count': count
            }), 200
        except Exception as db_error:
            logger.warning(f"Failed to clear history: {str(db_error)}")
            return jsonify({
                'success': False,
                'error': 'Failed to clear history'
            }), 500

    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
