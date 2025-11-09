/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BillingRecordDto } from './BillingRecordDto';
export type BillingRecordListDto = {
  billing_records: Array<BillingRecordDto>;
  skip: number;
  limit: number;
  total: number;
  has_previous: boolean;
  has_next: boolean;
};

