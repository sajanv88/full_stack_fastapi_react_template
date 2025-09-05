/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Permission } from './Permission';
import type { RoleType } from './RoleType';
export type Role = {
  id: string;
  name: RoleType;
  description?: (string | null);
  permissions?: (Array<Permission> | null);
  created_at: string;
};

