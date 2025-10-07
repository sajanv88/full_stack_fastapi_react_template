/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Gender } from './Gender';
import type { PydanticObjectId } from './PydanticObjectId';
export type CreateUserDto = {
  first_name: string;
  last_name: string;
  email: string;
  gender: Gender;
  tenant_id?: (PydanticObjectId | null);
  role_id?: (PydanticObjectId | null);
  password: string;
  sub_domain?: (string | null);
};

