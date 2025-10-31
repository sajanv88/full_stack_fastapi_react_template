/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RecurringDto } from './RecurringDto';
export type CreatePricingDto = {
  /**
   * Currency code, e.g., 'usd'
   */
  currency?: string;
  /**
   * A positive integer in cents (or 0 for a free price) representing how much to charge. One of unit_amount, unit_amount_decimal, or custom_unit_amount is required, unless billing_scheme=tiered.
   */
  unit_amount: number;
  /**
   * The ID of the product this price is associated with
   */
  product: string;
  /**
   * Whether the price is active or not
   */
  active?: boolean;
  recurring: RecurringDto;
};

