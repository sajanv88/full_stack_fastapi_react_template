/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContactInfo } from './ContactInfo';
import type { ThemeConfig } from './ThemeConfig';
export type BrandingDto = {
  id: string;
  logo_type: 'image/jpeg' | 'image/png';
  contact_info?: (ContactInfo | null);
  theme_config?: ThemeConfig;
  tenant_id: string;
  created_at: string;
  updated_at: string;
  app_name?: string;
  favicon_url?: (string | null);
};

