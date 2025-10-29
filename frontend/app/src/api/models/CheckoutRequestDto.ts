/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CheckoutRequestDto = {
  price_id: string;
  tenant_id?: (string | null);
  mode?: 'payment' | 'subscription' | 'setup';
  email: string;
};

