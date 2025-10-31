/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type PlanDto = {
  id: string;
  active: boolean;
  amount: number;
  amount_decimal: string;
  billing_scheme: string;
  currency?: string;
  interval: string;
  interval_count: number;
  product: string;
  trial_period_days?: (number | null);
  usage_type: string;
};

