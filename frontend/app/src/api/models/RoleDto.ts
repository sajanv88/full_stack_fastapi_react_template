/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Permission } from './Permission';
export type RoleDto = {
  id: string;
  name: string;
  description: (string | null);
  permissions?: Array<Permission>;
  created_at: string;
  updated_at: string;
  tenant_id?: (string | null);
};

