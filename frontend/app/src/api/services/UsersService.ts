/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_update_profile_picture_api_v1_users__user_id__update_profile_picture_put } from '../models/Body_update_profile_picture_api_v1_users__user_id__update_profile_picture_put';
import type { NewUser } from '../models/NewUser';
import type { ProfileImageUpdateResponse } from '../models/ProfileImageUpdateResponse';
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
  }: {
    skip?: number,
    limit?: number,
  }): CancelablePromise<UserListResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/users/',
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
   * Create User
   * @returns any Successful Response
   * @throws ApiError
   */
  public createUserApiV1UsersPost({
    requestBody,
  }: {
    requestBody: NewUser,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/users/',
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
  }: {
    userId: string,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/users/{user_id}',
      path: {
        'user_id': userId,
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
  }: {
    userId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/users/{user_id}',
      path: {
        'user_id': userId,
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
  }: {
    userId: string,
    requestBody: UserUpdate,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/users/{user_id}',
      path: {
        'user_id': userId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Profile Picture
   * @returns ProfileImageUpdateResponse Successful Response
   * @throws ApiError
   */
  public updateProfilePictureApiV1UsersUserIdUpdateProfilePicturePut({
    userId,
    formData,
  }: {
    userId: string,
    formData: Body_update_profile_picture_api_v1_users__user_id__update_profile_picture_put,
  }): CancelablePromise<ProfileImageUpdateResponse> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/users/{user_id}/update_profile_picture',
      path: {
        'user_id': userId,
      },
      formData: formData,
      mediaType: 'multipart/form-data',
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
  }: {
    userId: string,
    requestBody: UserRoleUpdateRequest,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/users/{user_id}/assign_role',
      path: {
        'user_id': userId,
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
  }: {
    userId: string,
    requestBody: UserRoleUpdateRequest,
  }): CancelablePromise<User> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/users/{user_id}/remove_role',
      path: {
        'user_id': userId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
