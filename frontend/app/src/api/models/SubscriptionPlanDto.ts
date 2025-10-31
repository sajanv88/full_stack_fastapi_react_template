/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type SubscriptionPlanDto = {
  id: string;
  /**
   * e.g., {'basic': 0, 'pro': 1, 'enterprise': 2}
   */
  plan_level: Record<string, number>;
  /**
   * Indicates if the subscription is a trial
   */
  is_trial: boolean;
  /**
   * The tenant who owns the subscription
   */
  tenant_id: (string | null);
  /**
   * who it is applied to, If end_user, then user_id must be set
   */
  actor: string;
  /**
   * The end user who has this subscription, if applicable
   */
  user_id: (string | null);
  /**
   * Corresponding Stripe Price ID
   */
  plan_id: string;
};

