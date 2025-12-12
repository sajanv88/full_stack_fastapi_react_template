/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Gender } from './Gender';
import type { RoleDto } from './RoleDto';
import type { SubscriptionPlanDto } from './SubscriptionPlanDto';
export type MeResponseDto = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  gender: Gender;
  role_id?: (string | null);
  is_active: boolean;
  activated_at?: (string | null);
  image_url?: (string | null);
  created_at: string;
  updated_at: string;
  tenant_id?: (string | null);
  sso_provider_id?: (string | null);
  role: RoleDto;
  subscription: (SubscriptionPlanDto | null);
};

