def dns_notification_email(user_first_name: str, hostname: str, status: str) -> str:
    """HTML email template for DNS configuration status."""
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">DNS Configuration Status</h2>
            <p>Hello {user_first_name},</p>
            <p>We wanted to inform you about the status of your DNS configuration:</p>
            <p>Status: {status}</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{hostname}" 
                style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    View DNS Configuration Details
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{hostname}</p>

           <p>If you have any questions or need further assistance, feel free to reach out to our support team.</p>
        </div>
    """