/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RecurringDto } from './RecurringDto';
export type PricingDto = {
  id: string;
  currency: string;
  unit_amount: number;
  product: string;
  active: boolean;
  recurring: RecurringDto;
  tax_behavior: string;
  type: string;
  unit_amount_decimal: string;
};

