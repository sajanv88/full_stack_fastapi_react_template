/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type RecurringDto = {
  /**
   * Billing interval, e.g., 'month'
   */
  interval?: 'day' | 'week' | 'month' | 'year';
  /**
   * Number of intervals between each billing cycle
   */
  interval_count?: number;
  /**
   * Configures how the quantity per period should be determined. Can be either metered or licensed. licensed automatically bills the quantity set when adding it to a subscription. metered aggregates the total usage based on usage records. Defaults to licensed.
   */
  usage_type?: 'licensed' | 'metered';
};

