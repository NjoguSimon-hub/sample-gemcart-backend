from flask import current_app
from flask_mail import Message
from app import mail
import sendgrid
from sendgrid.helpers.mail import Mail

def send_verification_email(email, username):
    """
    Send verification email to user
    """
    try:
        if current_app.config.get('SENDGRID_API_KEY'):
            # Use SendGrid
            sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])
            
            message = Mail(
                from_email=current_app.config['SENDGRID_FROM_EMAIL'],
                to_emails=email,
                subject='Welcome to GemCart - Verify Your Account',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #8b5cf6;">Welcome to GemCart! 💎</h2>
                    <p>Hello {username},</p>
                    <p>Thank you for joining GemCart, your premier destination for luxury jewelry!</p>
                    <p>Your account has been successfully created. You can now:</p>
                    <ul>
                        <li>Browse our exquisite jewelry collection</li>
                        <li>Add items to your wishlist</li>
                        <li>Place orders securely</li>
                        <li>Leave reviews for products</li>
                    </ul>
                    <p>Start exploring our collection of rings, necklaces, watches, and more!</p>
                    <p>Best regards,<br>The GemCart Team</p>
                </div>
                '''
            )
            
            response = sg.send(message)
            return response.status_code == 202
        else:
            # Fallback to Flask-Mail
            msg = Message(
                'Welcome to GemCart - Verify Your Account',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.html = f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #8b5cf6;">Welcome to GemCart! 💎</h2>
                <p>Hello {username},</p>
                <p>Thank you for joining GemCart!</p>
            </div>
            '''
            mail.send(msg)
            return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email: {str(e)}')
        return False

def send_order_confirmation(email, order):
    """
    Send order confirmation email
    """
    try:
        if current_app.config.get('SENDGRID_API_KEY'):
            sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])
            
            message = Mail(
                from_email=current_app.config['SENDGRID_FROM_EMAIL'],
                to_emails=email,
                subject=f'Order Confirmation - {order.order_number}',
                html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #8b5cf6;">Order Confirmation 📦</h2>
                    <p>Your order #{order.order_number} has been confirmed!</p>
                    <p><strong>Total: ${order.total_amount}</strong></p>
                    <p>We'll send you tracking information once your order ships.</p>
                    <p>Thank you for shopping with GemCart!</p>
                </div>
                '''
            )
            
            response = sg.send(message)
            return response.status_code == 202
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send order confirmation: {str(e)}')
        return False