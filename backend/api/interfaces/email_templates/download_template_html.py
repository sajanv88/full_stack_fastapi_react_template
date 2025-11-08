def download_template(user_first_name: str, link: str) -> str:
    """HTML email template for Download reports."""
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Download Report</h2>
            <p>Hello {user_first_name},</p>
            <p>We wanted to inform you that your download is ready:</p>
            
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{link}" 
                style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;"
                  target="_blank" rel="noopener" download>
                    Download Report
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{link}</p>

           <p>If you have any questions or need further assistance, feel free to reach out to our support team.</p>
        </div>
    """