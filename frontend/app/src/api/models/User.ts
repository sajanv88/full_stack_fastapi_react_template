/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Gender } from './Gender';
export type User = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  gender: Gender;
  role_id?: (string | null);
  is_active: boolean;
  activated_at?: (string | null);
  created_at: string;
  image_url?: (string | null);
  tenant_id?: (string | null);
};

