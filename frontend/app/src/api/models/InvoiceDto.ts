/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type InvoiceDto = {
  id: string;
  amount_country: string;
  account_name: string;
  amount_due?: number;
  amount_paid?: number;
  amount_remaining?: number;
  amount_overpaid?: number;
  attempt_count?: number;
  attempted?: boolean;
  auto_advance?: boolean;
  billing_reason: string;
  collection_method: string;
  created: number;
  currency: string;
  customer: string;
  customer_name: string;
  status: string;
  total: number;
  receipt_number?: (string | null);
};

