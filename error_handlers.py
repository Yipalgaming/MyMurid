"""
Error handling middleware for the Canteen Kiosk application.
"""

from flask import render_template, request, jsonify
import logging
from datetime import datetime

def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        if request.is_json:
            return jsonify({'error': 'Bad request', 'message': 'Invalid request data'}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        if request.is_json:
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        if request.is_json:
            return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        if request.is_json:
            return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(413)
    def too_large(error):
        """Handle 413 Request Entity Too Large errors"""
        if request.is_json:
            return jsonify({'error': 'File too large', 'message': 'File size exceeds limit'}), 413
        return render_template('errors/413.html'), 413
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle 429 Too Many Requests errors"""
        if request.is_json:
            return jsonify({'error': 'Too many requests', 'message': 'Rate limit exceeded'}), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        # Log the error
        app.logger.error(f'Server Error: {error}')
        
        if request.is_json:
            return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        # Log the error
        app.logger.error(f'Unhandled Exception: {error}', exc_info=True)
        
        if request.is_json:
            return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500
        return render_template('errors/500.html'), 500

def log_request_info():
    """Log request information for debugging"""
    app.logger.info(f'Request: {request.method} {request.url} from {request.remote_addr}')

def log_response_info(response):
    """Log response information for debugging"""
    app.logger.info(f'Response: {response.status_code} for {request.method} {request.url}')
    return response
