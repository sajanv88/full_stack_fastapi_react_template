/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Tenant } from '../models/Tenant';
import type { TenantListResponse } from '../models/TenantListResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class TenantsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Tenants
   * @returns TenantListResponse Successful Response
   * @throws ApiError
   */
  public getTenantsApiV1TenantsGet({
    skip,
    limit = 10,
  }: {
    skip?: number,
    limit?: number,
  }): CancelablePromise<TenantListResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/tenants/',
      query: {
        'skip': skip,
        'limit': limit,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create Tenant
   * @returns Tenant Successful Response
   * @throws ApiError
   */
  public createTenantApiV1TenantsPost({
    requestBody,
  }: {
    requestBody: Tenant,
  }): CancelablePromise<Tenant> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/tenants/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
