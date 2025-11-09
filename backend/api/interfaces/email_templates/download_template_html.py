def download_template(user_first_name: str) -> str:
    """HTML email template for Download reports."""
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Download Report</h2>
            <p>Hello {user_first_name},</p>
            <p>We wanted to inform you that your download is ready: It is <strong>attached</strong> to this email.</p>
            <p>Your audit logs report is attached to this email.</p>

           <p>If you have any questions or need further assistance, feel free to reach out to our support team.</p>
        </div>
    """