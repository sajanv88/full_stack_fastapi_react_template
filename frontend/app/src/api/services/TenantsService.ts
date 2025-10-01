/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateTenantDto } from '../models/CreateTenantDto';
import type { CreateTenantResponseDto } from '../models/CreateTenantResponseDto';
import type { TenantDto } from '../models/TenantDto';
import type { TenantListDto } from '../models/TenantListDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class TenantsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List Tenants
   * @returns TenantListDto Successful Response
   * @throws ApiError
   */
  public listTenantsApiV1TenantsGet({
    skip,
    limit = 10,
  }: {
    skip?: number,
    limit?: number,
  }): CancelablePromise<TenantListDto> {
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
   * @returns CreateTenantResponseDto Successful Response
   * @throws ApiError
   */
  public createTenantApiV1TenantsPost({
    requestBody,
  }: {
    requestBody: CreateTenantDto,
  }): CancelablePromise<CreateTenantResponseDto> {
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
  /**
   * Delete Tenant
   * @returns any Successful Response
   * @throws ApiError
   */
  public deleteTenantApiV1TenantsIdDelete({
    id,
  }: {
    id: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/tenants/{id}',
      path: {
        'id': id,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Search By Name
   * @returns TenantDto Successful Response
   * @throws ApiError
   */
  public searchByNameApiV1TenantsSearchByNameNameGet({
    name,
  }: {
    name: string,
  }): CancelablePromise<TenantDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/tenants/search_by_name/{name}',
      path: {
        'name': name,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Search By Subdomain
   * @returns TenantDto Successful Response
   * @throws ApiError
   */
  public searchBySubdomainApiV1TenantsSearchBySubdomainSubdomainGet({
    subdomain,
  }: {
    subdomain: string,
  }): CancelablePromise<TenantDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/tenants/search_by_subdomain/{subdomain}',
      path: {
        'subdomain': subdomain,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
