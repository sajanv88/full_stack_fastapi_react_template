from datetime import datetime
from typing import Literal, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field, field_serializer
from api.domain.entities.api_base_model import ApiBaseModel

class ThemeColors(BaseModel):
    """
    Represents the color palette for a specific mode (Light/Dark).
    Defaults here mirror the :root (Light Mode) values.
    """
    background: str = Field("oklch(1 0 0)", description="--background")
    foreground: str = Field("oklch(0.145 0 0)", description="--foreground")
    
    card: str = Field("oklch(1 0 0)", description="--card")
    card_foreground: str = Field("oklch(0.145 0 0)", description="--card-foreground")
    
    popover: str = Field("oklch(1 0 0)", description="--popover")
    popover_foreground: str = Field("oklch(0.145 0 0)", description="--popover-foreground")
    
    primary: str = Field("oklch(0.205 0 0)", description="--primary")
    primary_foreground: str = Field("oklch(0.985 0 0)", description="--primary-foreground")
    
    secondary: str = Field("oklch(0.97 0 0)", description="--secondary")
    secondary_foreground: str = Field("oklch(0.205 0 0)", description="--secondary-foreground")
    
    muted: str = Field("oklch(0.97 0 0)", description="--muted")
    muted_foreground: str = Field("oklch(0.556 0 0)", description="--muted-foreground")
    
    accent: str = Field("oklch(0.97 0 0)", description="--accent")
    accent_foreground: str = Field("oklch(0.205 0 0)", description="--accent-foreground")
    
    destructive: str = Field("oklch(0.577 0.245 27.325)", description="--destructive")
    destructive_foreground: str = Field("oklch(0.985 0 0)", description="Implied white for contrast")

    border: str = Field("oklch(0.922 0 0)", description="--border")
    input: str = Field("oklch(0.922 0 0)", description="--input")
    ring: str = Field("oklch(0.708 0 0)", description="--ring")
    
    # Charts
    chart_1: str = Field("oklch(0.646 0.222 41.116)", description="--chart-1")
    chart_2: str = Field("oklch(0.6 0.118 184.704)", description="--chart-2")
    chart_3: str = Field("oklch(0.398 0.07 227.392)", description="--chart-3")
    chart_4: str = Field("oklch(0.828 0.189 84.429)", description="--chart-4")
    chart_5: str = Field("oklch(0.769 0.188 70.08)", description="--chart-5")
    
    # Sidebar
    sidebar: str = Field("oklch(0.985 0 0)", description="--sidebar")
    sidebar_foreground: str = Field("oklch(0.145 0 0)", description="--sidebar-foreground")
    sidebar_primary: str = Field("oklch(0.205 0 0)", description="--sidebar-primary")
    sidebar_primary_foreground: str = Field("oklch(0.985 0 0)", description="--sidebar-primary-foreground")
    sidebar_accent: str = Field("oklch(0.97 0 0)", description="--sidebar-accent")
    sidebar_accent_foreground: str = Field("oklch(0.205 0 0)", description="--sidebar-accent-foreground")
    sidebar_border: str = Field("oklch(0.922 0 0)", description="--sidebar-border")
    sidebar_ring: str = Field("oklch(0.708 0 0)", description="--sidebar-ring")



def get_dark_theme_defaults():
    return ThemeColors(
        background="oklch(0.145 0 0)",
        foreground="oklch(0.985 0 0)",
        card="oklch(0.205 0 0)",
        card_foreground="oklch(0.985 0 0)",
        popover="oklch(0.205 0 0)",
        popover_foreground="oklch(0.985 0 0)",
        primary="oklch(0.922 0 0)",
        primary_foreground="oklch(0.205 0 0)",
        secondary="oklch(0.269 0 0)",
        secondary_foreground="oklch(0.985 0 0)",
        muted="oklch(0.269 0 0)",
        muted_foreground="oklch(0.708 0 0)",
        accent="oklch(0.269 0 0)",
        accent_foreground="oklch(0.985 0 0)",
        destructive="oklch(0.704 0.191 22.216)",
        destructive_foreground="oklch(0.985 0 0)",
        border="oklch(1 0 0 / 10%)",
        input="oklch(1 0 0 / 15%)",
        ring="oklch(0.556 0 0)",
        chart_1="oklch(0.488 0.243 264.376)",
        chart_2="oklch(0.696 0.17 162.48)",
        chart_3="oklch(0.769 0.188 70.08)",
        chart_4="oklch(0.627 0.265 303.9)",
        chart_5="oklch(0.645 0.246 16.439)",
        sidebar="oklch(0.205 0 0)",
        sidebar_foreground="oklch(0.985 0 0)",
        sidebar_primary="oklch(0.488 0.243 264.376)",
        sidebar_primary_foreground="oklch(0.985 0 0)",
        sidebar_accent="oklch(0.269 0 0)",
        sidebar_accent_foreground="oklch(0.985 0 0)",
        sidebar_border="oklch(1 0 0 / 10%)",
        sidebar_ring="oklch(0.556 0 0)"
    )

class ThemeConfig(BaseModel):
    """
    Master configuration containing global settings and specific mode palettes.
    """
    radius: str = Field("0.625rem", description="--radius")
    
    # Light mode defaults match the ThemeColors defaults
    light: ThemeColors = Field(default_factory=ThemeColors)
    
    # Dark mode defaults explicitly set to the .dark values provided
    dark: ThemeColors = Field(default_factory=get_dark_theme_defaults)
    
LogoType = Literal["image/jpeg", "image/png"]

class ContactInfo(BaseModel):
    support_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class Branding(ApiBaseModel):
    logo_url: Optional[str] = None
    logo_type: Optional[LogoType] = None
    favicon_url: Optional[str] = None
    app_name: str = "SaaS Org"
    contact_info: Optional[ContactInfo] = None
    theme_config: ThemeConfig = Field(default_factory=ThemeConfig)
    
    @field_serializer("id", "created_at", "updated_at", "tenant_id")
    def serialize_id(self, value: PydanticObjectId | datetime | None) -> str:
        if isinstance(value, PydanticObjectId):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        return value

    class Settings:
        name = "branding_configuration"
        indexes = ["tenant_id"]
