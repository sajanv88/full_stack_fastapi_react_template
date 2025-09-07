/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Role } from './Role';
export type UserMeResponse = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  gender: string;
  role?: (Role | null);
  is_active?: boolean;
  activated_at?: (string | null);
  image_url?: (string | null);
  tenant_id?: (string | null);
};

