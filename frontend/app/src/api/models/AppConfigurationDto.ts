/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BrandingDto } from './BrandingDto';
import type { TenantDto } from './TenantDto';
import type { UserPreferenceDto } from './UserPreferenceDto';
export type AppConfigurationDto = {
  is_multi_tenant_enabled: boolean;
  multi_tenancy_strategy: string;
  host_main_domain: string;
  is_user_logged_in?: (boolean | null);
  user_preferences?: (UserPreferenceDto | null);
  current_tenant?: (TenantDto | null);
  environment: string;
  enabled_sso_providers?: (Array<string> | null);
  branding?: (BrandingDto | null);
};

