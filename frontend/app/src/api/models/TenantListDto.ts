/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TenantDto } from './TenantDto';
export type TenantListDto = {
  tenants: Array<TenantDto>;
  skip: number;
  limit: number;
  total: number;
  hasPrevious: boolean;
  hasNext: boolean;
};

