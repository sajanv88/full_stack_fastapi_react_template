def activation_template_html(user_first_name: str, activation_link: str) -> str:
    """HTML email template for welcome newly created user or tenant."""
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Welcome to Full-Stack FastAPI React Template</h2>
            <p>Hello {user_first_name},</p>
            <p>Thank you for registering with us! To complete your registration and activate your account, please click the button below:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{activation_link}" 
                style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Activate Your Account
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{activation_link}</p>
            
            <p><strong>Note:</strong> This activation link will expire in 24 hours for security reasons.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                If you didn't create an account with us, please ignore this email.
            </p>
        </div>
    """