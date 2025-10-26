/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CreatePlanDto = {
  /**
   * Must be a supported currency: https://docs.stripe.com/currencies
   */
  currency?: string;
  interval: 'month' | 'year';
  /**
   * The product whose pricing the created plan will represent. This must be the ID of an existing product.
   */
  product_id: string;
  amount: number;
};

