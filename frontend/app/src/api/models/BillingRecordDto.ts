/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type BillingRecordDto = {
  scope: 'host' | 'tenant';
  actor: 'tenant' | 'end_user';
  user_id?: (string | null);
  payment_type: 'one_time' | 'recurring' | 'both';
  currency: string;
  amount?: (number | null);
  stripe_customer_id?: (string | null);
  stripe_subscription_id?: (string | null);
  stripe_session_id?: (string | null);
  product_id?: (string | null);
  price_id?: (string | null);
  status: 'pending' | 'requires_payment_method' | 'requires_action' | 'active' | 'succeeded' | 'payment_failed' | 'canceled' | 'incomplete';
  current_period_end?: (number | null);
  canceled_at?: (number | null);
  cancellation_reason?: (string | null);
  metadata?: (Record<string, string> | null);
};

