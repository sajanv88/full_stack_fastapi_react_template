def email_changes_confirmation_template_html(user_first_name: str, email_change_link: str) -> str:
    """
    HTML email template for confirming email changes.
    """
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Notification!</h2>
            <p>Hello {user_first_name},</p>
            <p>You have recently requested to change your email. Please click the button below to confirm your new email address:</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{email_change_link}" 
                style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Confirm Your New Email
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{email_change_link}</p>

            <p><strong>Note:</strong> This activation link will expire in 24 hours for security reasons.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                If you didn't create an account with us, please ignore this email.
            </p>
        </div>
    """