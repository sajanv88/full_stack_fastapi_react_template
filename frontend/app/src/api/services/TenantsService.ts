/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateTenantDto } from '../models/CreateTenantDto';
import type { CreateTenantResponseDto } from '../models/CreateTenantResponseDto';
import type { FeatureDto } from '../models/FeatureDto';
import type { SubdomainAvailabilityDto } from '../models/SubdomainAvailabilityDto';
import type { TenantDto } from '../models/TenantDto';
import type { TenantListDto } from '../models/TenantListDto';
import type { UpdateTenantDto } from '../models/UpdateTenantDto';
import type { UpdateTenantResponseDto } from '../models/UpdateTenantResponseDto';
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
  /**
   * Check Subdomain Availability
   * @returns SubdomainAvailabilityDto Successful Response
   * @throws ApiError
   */
  public checkSubdomainAvailabilityApiV1TenantsCheckSubdomainSubdomainGet({
    subdomain,
  }: {
    subdomain: string,
  }): CancelablePromise<SubdomainAvailabilityDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/tenants/check_subdomain/{subdomain}',
      path: {
        'subdomain': subdomain,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Tenant Dns Record
   * When bringing your own domain you must map the DNS records for your custom domain to point to our main domain.
   * You can do this by adding a CNAME record in your domain's DNS settings.
   * Here is an example of how to set it up:
   * Type: CNAME
   * Name: app
   * Value: demo.dev.xyz
   * @returns UpdateTenantResponseDto Successful Response
   * @throws ApiError
   */
  public updateTenantDnsRecordApiV1TenantsUpdateDnsTenantIdPost({
    tenantId,
    requestBody,
  }: {
    tenantId: string,
    requestBody: UpdateTenantDto,
  }): CancelablePromise<UpdateTenantResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/tenants/update_dns/{tenant_id}',
      path: {
        'tenant_id': tenantId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Check Dns Status
   * @returns UpdateTenantResponseDto Successful Response
   * @throws ApiError
   */
  public checkDnsStatusApiV1TenantsCheckDnsTenantIdGet({
    tenantId,
  }: {
    tenantId: string,
  }): CancelablePromise<UpdateTenantResponseDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/tenants/check_dns/{tenant_id}',
      path: {
        'tenant_id': tenantId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Get Tenant Features
   * @returns FeatureDto Successful Response
   * @throws ApiError
   */
  public getTenantFeaturesApiV1TenantsTenantIdFeaturesGet({
    tenantId,
  }: {
    tenantId: string,
  }): CancelablePromise<Array<FeatureDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/tenants/{tenant_id}/features',
      path: {
        'tenant_id': tenantId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Tenant Feature
   * @returns UpdateTenantResponseDto Successful Response
   * @throws ApiError
   */
  public updateTenantFeatureApiV1TenantsTenantIdUpdateFeaturePatch({
    tenantId,
    requestBody,
  }: {
    tenantId: string,
    requestBody: FeatureDto,
  }): CancelablePromise<UpdateTenantResponseDto> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/tenants/{tenant_id}/update_feature',
      path: {
        'tenant_id': tenantId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
