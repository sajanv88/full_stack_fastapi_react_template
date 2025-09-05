/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DashboardMetrics } from '../models/DashboardMetrics';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DashboardService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Dashboard Metrics
   * @returns DashboardMetrics Successful Response
   * @throws ApiError
   */
  public getDashboardMetricsApiV1DashboardGet({
    filter = 'all',
  }: {
    filter?: 'today' | 'this_week' | 'last_3_months' | 'all',
  }): CancelablePromise<DashboardMetrics> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/dashboard/',
      query: {
        'filter': filter,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
