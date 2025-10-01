/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Permission } from './Permission';
import type { PydanticObjectId } from './PydanticObjectId';
export type UpdateRoleDto = {
  name: string;
  description?: (string | null);
  tenant_id?: (PydanticObjectId | null);
  permissions?: Array<Permission>;
};

