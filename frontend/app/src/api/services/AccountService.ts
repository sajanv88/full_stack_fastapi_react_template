/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_login_api_v1_account_login_post } from '../models/Body_login_api_v1_account_login_post';
import type { Body_passkey_login_api_v1_account_passkey_login_post } from '../models/Body_passkey_login_api_v1_account_passkey_login_post';
import type { Body_passkey_register_api_v1_account_passkey_register_post } from '../models/Body_passkey_register_api_v1_account_passkey_register_post';
import type { ChangeEmailConfirmRequestDto } from '../models/ChangeEmailConfirmRequestDto';
import type { ChangeEmailRequestDto } from '../models/ChangeEmailRequestDto';
import type { ChangeEmailResponseDto } from '../models/ChangeEmailResponseDto';
import type { CreateUserDto } from '../models/CreateUserDto';
import type { HasPasskeysDto } from '../models/HasPasskeysDto';
import type { MagicLinkResponseDto } from '../models/MagicLinkResponseDto';
import type { MeResponseDto } from '../models/MeResponseDto';
import type { PasswordResetConfirmRequestDto } from '../models/PasswordResetConfirmRequestDto';
import type { PasswordResetRequestDto } from '../models/PasswordResetRequestDto';
import type { PasswordResetResponseDto } from '../models/PasswordResetResponseDto';
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
   * Refresh Token
   * @returns TokenSetDto Successful Response
   * @throws ApiError
   */
  public refreshTokenApiV1AccountRefreshPost({
    refreshToken,
  }: {
    refreshToken?: (string | null),
  }): CancelablePromise<TokenSetDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/refresh',
      cookies: {
        'refresh_token': refreshToken,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Logout
   * @returns any Successful Response
   * @throws ApiError
   */
  public logoutApiV1AccountLogoutGet(): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/account/logout',
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
    tenantId,
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
    /**
     * The tenant ID associated with the user, if applicable
     */
    tenantId?: (string | null),
  }): CancelablePromise<PasswordResetResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/password_reset_confirmation',
      query: {
        'token': token,
        'user_id': userId,
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
    tenantId,
  }: {
    requestBody: UserActivationRequestDto,
    /**
     * The tenant ID associated with the user, if applicable
     */
    tenantId?: (string | null),
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/activate',
      query: {
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
  /**
   * Passkey Register Options
   * @returns any Successful Response
   * @throws ApiError
   */
  public passkeyRegisterOptionsApiV1AccountPasskeyRegisterOptionsPost({
    requestBody,
  }: {
    requestBody: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/passkey/register_options',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Passkey Register
   * @returns any Successful Response
   * @throws ApiError
   */
  public passkeyRegisterApiV1AccountPasskeyRegisterPost({
    requestBody,
  }: {
    requestBody: Body_passkey_register_api_v1_account_passkey_register_post,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/passkey/register',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Passkey Login Options
   * @returns any Successful Response
   * @throws ApiError
   */
  public passkeyLoginOptionsApiV1AccountPasskeyLoginOptionsPost({
    requestBody,
  }: {
    requestBody: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/passkey/login_options',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Passkey Login
   * @returns TokenSetDto Successful Response
   * @throws ApiError
   */
  public passkeyLoginApiV1AccountPasskeyLoginPost({
    requestBody,
  }: {
    requestBody: Body_passkey_login_api_v1_account_passkey_login_post,
  }): CancelablePromise<TokenSetDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/passkey/login',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Has Passkeys
   * @returns HasPasskeysDto Successful Response
   * @throws ApiError
   */
  public hasPasskeysApiV1AccountPasskeyHasPasskeysPost({
    requestBody,
  }: {
    requestBody: string,
  }): CancelablePromise<HasPasskeysDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/passkey/has_passkeys',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Email Magic Link Login
   * @returns MagicLinkResponseDto Successful Response
   * @throws ApiError
   */
  public emailMagicLinkLoginApiV1AccountEmailMagicLinkLoginPost({
    requestBody,
  }: {
    requestBody: string,
  }): CancelablePromise<MagicLinkResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/account/email_magic_link_login',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Email Magic Link Validate
   * @returns TokenSetDto Successful Response
   * @throws ApiError
   */
  public emailMagicLinkValidateApiV1AccountEmailMagicLinkValidateGet({
    token,
    userId,
    tenantId,
  }: {
    /**
     * The magic link token
     */
    token: string,
    /**
     * The user ID associated with the token
     */
    userId: string,
    /**
     * The tenant ID associated with the user, if applicable
     */
    tenantId?: (string | null),
  }): CancelablePromise<TokenSetDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/account/email_magic_link_validate',
      query: {
        'token': token,
        'user_id': userId,
        'tenant_id': tenantId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
