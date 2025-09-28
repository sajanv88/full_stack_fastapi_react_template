

def password_reset_email_template_html(user_first_name: str, password_reset_link: str) -> str:
    """
    HTML email template for password reset.
    """
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Password Reset Request</h2>
            <p>Hello {user_first_name},</p>
            <p>We received a request to reset your password. Click the button below to reset it:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{password_reset_link}" 
                style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Your Password
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{password_reset_link}</p>
            
            <p><strong>Note:</strong> This password reset link will expire in 24 hours for security reasons.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                If you didn't request a password reset, please ignore this email.
            </p>
        </div>
    """