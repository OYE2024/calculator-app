"""
Simple Online Calculator Web Application
Saves calculation history to database
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
db_user = os.environ.get('RDS_USERNAME', 'admin')
db_password = os.environ.get('RDS_PASSWORD', 'password')
db_host = os.environ.get('RDS_HOSTNAME', 'localhost')
db_port = os.environ.get('RDS_PORT', '5432')
db_name = os.environ.get('RDS_DB_NAME', 'calculator_db')

# SQLAlchemy configuration
database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize database
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

# Create tables on startup
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# Routes
@app.route('/')
def index():
    """Main page with calculator interface"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Elastic Beanstalk"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint for calculation"""
    try:
        data = request.json
        expression = data.get('expression', '').strip()

        # Validate input
        if not expression:
            return jsonify({'error': 'Expression is empty'}), 400

        # Simple validation: allow only numbers, operators, and parentheses
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return jsonify({'error': 'Invalid characters in expression'}), 400

        # Evaluate expression safely
        try:
            result = eval(expression)
            if not isinstance(result, (int, float)):
                return jsonify({'error': 'Invalid expression'}), 400
        except Exception as e:
            return jsonify({'error': f'Invalid expression: {str(e)}'}), 400

        # Get user IP
        user_ip = request.remote_addr

        # Save to database
        calculation = Calculation(
            expression=expression,
            result=result,
            user_ip=user_ip
        )
        db.session.add(calculation)
        db.session.commit()

        logger.info(f"Calculation saved: {expression} = {result}")

        return jsonify({
            'expression': expression,
            'result': result,
            'id': calculation.id
        }), 200

    except Exception as e:
        logger.error(f"Error in calculate endpoint: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """API endpoint to get calculation history"""
    try:
        limit = request.args.get('limit', 20, type=int)

        calculations = Calculation.query.order_by(
            Calculation.timestamp.desc()
        ).limit(limit).all()

        return jsonify([calc.to_dict() for calc in calculations]), 200

    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<int:calculation_id>', methods=['DELETE'])
def delete_calculation(calculation_id):
    """API endpoint to delete a calculation"""
    try:
        calculation = Calculation.query.get(calculation_id)

        if not calculation:
            return jsonify({'error': 'Calculation not found'}), 404

        db.session.delete(calculation)
        db.session.commit()

        logger.info(f"Calculation {calculation_id} deleted")

        return jsonify({'message': 'Calculation deleted'}), 200

    except Exception as e:
        logger.error(f"Error deleting calculation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """API endpoint to get calculation statistics"""
    try:
        total_calculations = Calculation.query.count()

        if total_calculations == 0:
            return jsonify({
                'total_calculations': 0,
                'average_result': 0,
                'min_result': None,
                'max_result': None
            }), 200

        from sqlalchemy import func

        stats = db.session.query(
            func.count(Calculation.id).label('total'),
            func.avg(Calculation.result).label('average'),
            func.min(Calculation.result).label('min'),
            func.max(Calculation.result).label('max')
        ).first()

        return jsonify({
            'total_calculations': stats.total or 0,
            'average_result': float(stats.average or 0),
            'min_result': float(stats.min or 0),
            'max_result': float(stats.max or 0)
        }), 200

    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=False, host='0.0.0.0', port=5000)
