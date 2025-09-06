/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NewRole } from '../models/NewRole';
import type { Role } from '../models/Role';
import type { RoleListResponse } from '../models/RoleListResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class RolesService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Roles
   * @returns RoleListResponse Successful Response
   * @throws ApiError
   */
  public getRolesApiV1RolesGet({
    skip,
    limit = 10,
    resourceId,
  }: {
    skip?: number,
    limit?: number,
    resourceId?: string,
  }): CancelablePromise<RoleListResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/roles/',
      query: {
        'skip': skip,
        'limit': limit,
        'resource_id': resourceId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create Role
   * @returns any Successful Response
   * @throws ApiError
   */
  public createRoleApiV1RolesPost({
    requestBody,
    resourceId,
  }: {
    requestBody: NewRole,
    resourceId?: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/roles/',
      query: {
        'resource_id': resourceId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Get Role
   * @returns Role Successful Response
   * @throws ApiError
   */
  public getRoleApiV1RolesRoleIdGet({
    roleId,
    resourceId,
  }: {
    roleId: string,
    resourceId?: string,
  }): CancelablePromise<Role> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/roles/{role_id}',
      path: {
        'role_id': roleId,
      },
      query: {
        'resource_id': resourceId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete Role
   * @returns any Successful Response
   * @throws ApiError
   */
  public deleteRoleApiV1RolesRoleIdDelete({
    roleId,
    resourceId,
  }: {
    roleId: string,
    resourceId?: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/roles/{role_id}',
      path: {
        'role_id': roleId,
      },
      query: {
        'resource_id': resourceId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Role
   * @returns Role Successful Response
   * @throws ApiError
   */
  public updateRoleApiV1RolesRoleIdPut({
    roleId,
    requestBody,
    resourceId,
  }: {
    roleId: string,
    requestBody: NewRole,
    resourceId?: string,
  }): CancelablePromise<Role> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/roles/{role_id}',
      path: {
        'role_id': roleId,
      },
      query: {
        'resource_id': resourceId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
