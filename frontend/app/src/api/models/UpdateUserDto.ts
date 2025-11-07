/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Gender } from './Gender';
import type { PydanticObjectId } from './PydanticObjectId';
export type UpdateUserDto = {
  first_name?: (string | null);
  last_name?: (string | null);
  email?: (string | null);
  gender?: (Gender | null);
  image_url?: (string | null);
  role_id?: (string | null);
  is_active?: (boolean | null);
  tenant_id?: (PydanticObjectId | null);
};

