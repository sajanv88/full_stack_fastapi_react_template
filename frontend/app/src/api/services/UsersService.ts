/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_update_profile_picture_api_v1_users__user_id__update_profile_picture_put } from '../models/Body_update_profile_picture_api_v1_users__user_id__update_profile_picture_put';
import type { CreateUserDto } from '../models/CreateUserDto';
import type { CreateUserResponseDto } from '../models/CreateUserResponseDto';
import type { UpdateUserDto } from '../models/UpdateUserDto';
import type { UserDto } from '../models/UserDto';
import type { UserListDto } from '../models/UserListDto';
import type { UserProfileImageUpdateDto } from '../models/UserProfileImageUpdateDto';
import type { UserRoleUpdateRequestDto } from '../models/UserRoleUpdateRequestDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class UsersService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List Users
   * @returns UserListDto Successful Response
   * @throws ApiError
   */
  public listUsersApiV1UsersGet({
    skip,
    limit = 10,
  }: {
    skip?: number,
    limit?: number,
  }): CancelablePromise<UserListDto> {
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
   * @returns CreateUserResponseDto Successful Response
   * @throws ApiError
   */
  public createUserApiV1UsersPost({
    requestBody,
  }: {
    requestBody: CreateUserDto,
  }): CancelablePromise<CreateUserResponseDto> {
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
   * @returns UserDto Successful Response
   * @throws ApiError
   */
  public getUserApiV1UsersUserIdGet({
    userId,
  }: {
    userId: string,
  }): CancelablePromise<UserDto> {
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
   * Update User
   * @returns UserDto Successful Response
   * @throws ApiError
   */
  public updateUserApiV1UsersUserIdPut({
    userId,
    requestBody,
  }: {
    userId: string,
    requestBody: UpdateUserDto,
  }): CancelablePromise<UserDto> {
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
   * Get Profile Image
   * @returns UserProfileImageUpdateDto Successful Response
   * @throws ApiError
   */
  public getProfileImageApiV1UsersProfileImageKeyGet({
    imageKey,
  }: {
    imageKey: string,
  }): CancelablePromise<UserProfileImageUpdateDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/users/profile/{image_key}',
      path: {
        'image_key': imageKey,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Profile Picture
   * @returns UserProfileImageUpdateDto Successful Response
   * @throws ApiError
   */
  public updateProfilePictureApiV1UsersUserIdUpdateProfilePicturePut({
    userId,
    formData,
  }: {
    userId: string,
    formData: Body_update_profile_picture_api_v1_users__user_id__update_profile_picture_put,
  }): CancelablePromise<UserProfileImageUpdateDto> {
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
   * @returns UserDto Successful Response
   * @throws ApiError
   */
  public patchUserApiV1UsersUserIdAssignRolePatch({
    userId,
    requestBody,
  }: {
    userId: string,
    requestBody: UserRoleUpdateRequestDto,
  }): CancelablePromise<UserDto> {
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
   * @returns UserDto Successful Response
   * @throws ApiError
   */
  public removeUserRoleApiV1UsersUserIdRemoveRolePatch({
    userId,
    requestBody,
  }: {
    userId: string,
    requestBody: UserRoleUpdateRequestDto,
  }): CancelablePromise<UserDto> {
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
