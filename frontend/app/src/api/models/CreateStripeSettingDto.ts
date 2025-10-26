/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type CreateStripeSettingDto = {
  default_currency?: string;
  stripe_webhook_secret: string;
  mode?: 'one_time' | 'recurring' | 'both';
  trial_period_days?: number;
  stripe_secret_key: string;
};

