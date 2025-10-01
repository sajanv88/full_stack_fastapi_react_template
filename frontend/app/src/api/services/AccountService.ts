/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_api_v1_account_login_post } from '../models/Body_login_api_v1_account_login_post';
import type { ChangeEmailConfirmRequestDto } from '../models/ChangeEmailConfirmRequestDto';
import type { ChangeEmailRequestDto } from '../models/ChangeEmailRequestDto';
import type { ChangeEmailResponseDto } from '../models/ChangeEmailResponseDto';
import type { CreateUserDto } from '../models/CreateUserDto';
import type { MeResponseDto } from '../models/MeResponseDto';
import type { PasswordResetConfirmRequestDto } from '../models/PasswordResetConfirmRequestDto';
import type { PasswordResetRequestDto } from '../models/PasswordResetRequestDto';
import type { PasswordResetResponseDto } from '../models/PasswordResetResponseDto';
import type { TokenRefreshRequestDto } from '../models/TokenRefreshRequestDto';
import type { TokenSetDto } from '../models/TokenSetDto';
import type { UserActivationRequestDto } from '../models/UserActivationRequestDto';
import type { UserResendActivationEmailRequestDto } from '../models/UserResendActivationEmailRequestDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AccountService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Login
   * @returns TokenSetDto Successful Response
   * @throws ApiError
   */
  public loginApiV1AccountLoginPost({
    formData,
  }: {
    formData: Body_login_api_v1_account_login_post,
  }): CancelablePromise<TokenSetDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/login',
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
  public registerApiV1AccountRegisterPost({
    requestBody,
  }: {
    requestBody: CreateUserDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/register',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Read Users Me
   * @returns MeResponseDto Successful Response
   * @throws ApiError
   */
  public readUsersMeApiV1AccountMeGet(): CancelablePromise<MeResponseDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/account/me',
    });
  }
  /**
   * Refresh Token
   * @returns TokenSetDto Successful Response
   * @throws ApiError
   */
  public refreshTokenApiV1AccountRefreshPost({
    requestBody,
  }: {
    requestBody: TokenRefreshRequestDto,
  }): CancelablePromise<TokenSetDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/refresh',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Password Reset Request
   * @returns PasswordResetResponseDto Successful Response
   * @throws ApiError
   */
  public passwordResetRequestApiV1AccountPasswordResetRequestPost({
    requestBody,
  }: {
    requestBody: PasswordResetRequestDto,
  }): CancelablePromise<PasswordResetResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/password_reset_request',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Password Reset Confirm
   * @returns PasswordResetResponseDto Successful Response
   * @throws ApiError
   */
  public passwordResetConfirmApiV1AccountPasswordResetConfirmationPost({
    token,
    userId,
    requestBody,
  }: {
    /**
     * The password reset token
     */
    token: string,
    /**
     * The user ID associated with the token
     */
    userId: string,
    requestBody: PasswordResetConfirmRequestDto,
  }): CancelablePromise<PasswordResetResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/password_reset_confirmation',
      query: {
        'token': token,
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
   * Resend Activation Email
   * @returns any Successful Response
   * @throws ApiError
   */
  public resendActivationEmailApiV1AccountResendActivationEmailPost({
    requestBody,
  }: {
    requestBody: UserResendActivationEmailRequestDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/resend_activation_email',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Activate Account
   * @returns any Successful Response
   * @throws ApiError
   */
  public activateAccountApiV1AccountActivatePost({
    requestBody,
  }: {
    requestBody: UserActivationRequestDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/activate',
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
  public changeEmailApiV1AccountChangeEmailRequestPatch({
    requestBody,
  }: {
    requestBody: ChangeEmailRequestDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/account/change_email_request',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Change Email Confirmation
   * @returns ChangeEmailResponseDto Successful Response
   * @throws ApiError
   */
  public changeEmailConfirmationApiV1AccountChangeEmailConfirmationPatch({
    requestBody,
  }: {
    requestBody: ChangeEmailConfirmRequestDto,
  }): CancelablePromise<ChangeEmailResponseDto> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/account/change_email_confirmation',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
