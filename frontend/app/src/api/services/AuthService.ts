/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivationRequest } from '../models/ActivationRequest';
import type { Body_login_api_v1_auth_login_post } from '../models/Body_login_api_v1_auth_login_post';
import type { NewUser } from '../models/NewUser';
import type { RefreshRequest } from '../models/RefreshRequest';
import type { TokenSet } from '../models/TokenSet';
import type { UserEmailUpdate } from '../models/UserEmailUpdate';
import type { UserMeResponse } from '../models/UserMeResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuthService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Login
   * @returns TokenSet Successful Response
   * @throws ApiError
   */
  public loginApiV1AuthLoginPost({
    formData,
  }: {
    formData: Body_login_api_v1_auth_login_post,
  }): CancelablePromise<TokenSet> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/auth/login',
      formData: formData,
      mediaType: 'application/x-www-form-urlencoded',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Register
   * @returns any Successful Response
   * @throws ApiError
   */
  public registerApiV1AuthRegisterPost({
    requestBody,
  }: {
    requestBody: NewUser,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/auth/register',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Read Users Me
   * @returns UserMeResponse Successful Response
   * @throws ApiError
   */
  public readUsersMeApiV1AuthMeGet(): CancelablePromise<UserMeResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/auth/me',
    });
  }
  /**
   * Refresh Token
   * @returns TokenSet Successful Response
   * @throws ApiError
   */
  public refreshTokenApiV1AuthRefreshPost({
    requestBody,
  }: {
    requestBody: RefreshRequest,
  }): CancelablePromise<TokenSet> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/auth/refresh',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Change Email
   * @returns any Successful Response
   * @throws ApiError
   */
  public changeEmailApiV1AuthChangeEmailPatch({
    requestBody,
  }: {
    requestBody: UserEmailUpdate,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/auth/change-email',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Activate Account
   * Activate user account using the activation token.
   * @returns any Successful Response
   * @throws ApiError
   */
  public activateAccountApiV1AuthActivatePost({
    requestBody,
  }: {
    requestBody: ActivationRequest,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/auth/activate',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
