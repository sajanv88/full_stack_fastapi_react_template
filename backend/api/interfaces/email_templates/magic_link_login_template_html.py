def magic_link_login_template(user_first_name: str, magic_link: str) -> str:
    """HTML email template for magic link login."""
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Welcome to Full-Stack FastAPI React Template</h2>
            <p>Hello {user_first_name},</p>
            <p>To log in to your account, please click the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{magic_link}" 
                style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Log In to Your Account
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{magic_link}</p>

            <p><strong>Note:</strong> This magic link will expire in 5 minutes for security reasons.</p>
        
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                If you didn't create an account with us, please ignore this email.
            </p>
        </div>
    """