def tenant_subdomain_active_html(subdomain_link: str) -> str:
    """HTML email template for tenant subdomain activation."""
    return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Your subdomain is ready!</h2>
            
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{subdomain_link}" 
                style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Visit Now
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <p style="word-break: break-all; color: #007bff;">{subdomain_link}</p>
        </div>
    """