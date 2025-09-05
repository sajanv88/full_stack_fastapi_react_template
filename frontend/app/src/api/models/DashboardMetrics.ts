/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type DashboardMetrics = {
  filter: 'today' | 'this_week' | 'last_3_months' | 'all';
  joined_users: number;
  total_users: number;
  timeseries: Array<Record<string, any>>;
};

