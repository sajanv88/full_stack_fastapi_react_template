/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FeatureDto } from './FeatureDto';
export type TenantDto = {
  id: (string | null);
  name: string;
  subdomain: (string | null);
  is_active: boolean;
  custom_domain: (string | null);
  custom_domain_status?: 'active' | 'failed' | 'activation-progress';
  features?: Array<FeatureDto>;
};

