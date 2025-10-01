/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateRoleDto } from '../models/CreateRoleDto';
import type { CreateRoleResponseDto } from '../models/CreateRoleResponseDto';
import type { RoleDto } from '../models/RoleDto';
import type { RoleListDto } from '../models/RoleListDto';
import type { UpdateRoleDto } from '../models/UpdateRoleDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class RolesService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List Roles
   * @returns RoleListDto Successful Response
   * @throws ApiError
   */
  public listRolesApiV1RolesGet({
    skip,
    limit = 10,
  }: {
    skip?: number,
    limit?: number,
  }): CancelablePromise<RoleListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/roles/',
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
   * Create Role
   * @returns CreateRoleResponseDto Successful Response
   * @throws ApiError
   */
  public createRoleApiV1RolesPost({
    requestBody,
  }: {
    requestBody: CreateRoleDto,
  }): CancelablePromise<CreateRoleResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/roles/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Search Role By Name
   * @returns RoleDto Successful Response
   * @throws ApiError
   */
  public searchRoleByNameApiV1RolesSearchByNameGet({
    name,
  }: {
    name: string,
  }): CancelablePromise<Array<RoleDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/roles/search_by_name',
      query: {
        'name': name,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Get Role
   * @returns RoleDto Successful Response
   * @throws ApiError
   */
  public getRoleApiV1RolesRoleIdGet({
    roleId,
  }: {
    roleId: string,
  }): CancelablePromise<RoleDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/roles/{role_id}',
      path: {
        'role_id': roleId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Role
   * @returns RoleDto Successful Response
   * @throws ApiError
   */
  public updateRoleApiV1RolesRoleIdPut({
    roleId,
    requestBody,
  }: {
    roleId: string,
    requestBody: UpdateRoleDto,
  }): CancelablePromise<RoleDto> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/roles/{role_id}',
      path: {
        'role_id': roleId,
      },
      body: requestBody,
      mediaType: 'application/json',
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
  }: {
    roleId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/roles/{role_id}',
      path: {
        'role_id': roleId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
