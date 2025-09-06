/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NewUser } from '../models/NewUser';
import type { User } from '../models/User';
import type { UserListResponse } from '../models/UserListResponse';
import type { UserRoleUpdateRequest } from '../models/UserRoleUpdateRequest';
import type { UserUpdate } from '../models/UserUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class UsersService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Users
   * @returns UserListResponse Successful Response
   * @throws ApiError
   */
  public getUsersApiV1UsersGet({
    skip,
    limit = 10,
    resourceId,
  }: {
    skip?: number,
    limit?: number,
    resourceId?: string,
  }): CancelablePromise<UserListResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/users/',
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
   * Create User
   * @returns any Successful Response
   * @throws ApiError
   */
  public createUserApiV1UsersPost({
    requestBody,
    resourceId,
  }: {
    requestBody: NewUser,
    resourceId?: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/users/',
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
   * Get User
   * @returns User Successful Response
   * @throws ApiError
   */
  public getUserApiV1UsersUserIdGet({
    userId,
    resourceId,
  }: {
    userId: string,
    resourceId?: string,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/users/{user_id}',
      path: {
        'user_id': userId,
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
   * Delete User
   * @returns any Successful Response
   * @throws ApiError
   */
  public deleteUserApiV1UsersUserIdDelete({
    userId,
    resourceId,
  }: {
    userId: string,
    resourceId?: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/users/{user_id}',
      path: {
        'user_id': userId,
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
   * Update User
   * @returns User Successful Response
   * @throws ApiError
   */
  public updateUserApiV1UsersUserIdPut({
    userId,
    requestBody,
    resourceId,
  }: {
    userId: string,
    requestBody: UserUpdate,
    resourceId?: string,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/users/{user_id}',
      path: {
        'user_id': userId,
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
  /**
   * Patch User
   * @returns User Successful Response
   * @throws ApiError
   */
  public patchUserApiV1UsersUserIdAssignRolePatch({
    userId,
    requestBody,
    resourceId,
  }: {
    userId: string,
    requestBody: UserRoleUpdateRequest,
    resourceId?: string,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/users/{user_id}/assign_role',
      path: {
        'user_id': userId,
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
  /**
   * Remove User Role
   * @returns User Successful Response
   * @throws ApiError
   */
  public removeUserRoleApiV1UsersUserIdRemoveRolePatch({
    userId,
    requestBody,
    resourceId,
  }: {
    userId: string,
    requestBody: UserRoleUpdateRequest,
    resourceId?: string,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/users/{user_id}/remove_role',
      path: {
        'user_id': userId,
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
