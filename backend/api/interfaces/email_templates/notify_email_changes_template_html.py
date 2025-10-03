def notify_email_change_template_html(user_first_name: str) -> str:
    """
    HTML email template for notifying users about their new email changes.
    """
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Email has been Changed Successfully</h2>
            <p>Hello {user_first_name},</p>
            <p>This is a confirmation that your email has been successfully changed.</p>

            <p>If you did not make this change, please contact our support team immediately.</p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                If you didn't request an email change, please contact support immediately.
            </p>
        </div>
    """