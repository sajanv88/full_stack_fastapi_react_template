/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserDto } from './UserDto';
export type UserListDto = {
  users: Array<UserDto>;
  skip: number;
  limit: number;
  total: number;
  hasPrevious: boolean;
  hasNext: boolean;
};

