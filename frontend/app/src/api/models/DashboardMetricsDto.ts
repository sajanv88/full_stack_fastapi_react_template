/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimeSeriesDto } from './TimeSeriesDto';
export type DashboardMetricsDto = {
  filter: 'today' | 'this_week' | 'last_3_months' | 'all';
  joined_users: number;
  total_users: number;
  timeseries: Array<TimeSeriesDto>;
};

