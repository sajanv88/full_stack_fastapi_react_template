/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContactInfo } from './ContactInfo';
import type { IdentityDto } from './IdentityDto';
import type { ThemeConfig } from './ThemeConfig';
export type UpdateBrandingDto = {
  identity?: (IdentityDto | null);
  contact_info?: (ContactInfo | null);
  theme_config?: (ThemeConfig | null);
  tenant_id?: (string | null);
  logo_url?: (string | null);
  logo_type?: ('image/jpeg' | 'image/png' | null);
};

