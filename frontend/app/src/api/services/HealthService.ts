/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HealthCheckResponseDto } from '../models/HealthCheckResponseDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class HealthService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Health Check
   * @returns HealthCheckResponseDto Successful Response
   * @throws ApiError
   */
  public healthCheckApiV1HealthGet(): CancelablePromise<HealthCheckResponseDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/health/',
    });
  }
}
