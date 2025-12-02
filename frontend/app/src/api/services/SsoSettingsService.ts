/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateSSOSettingsDto } from '../models/CreateSSOSettingsDto';
import type { ReadSSOSettingsDto } from '../models/ReadSSOSettingsDto';
import type { SSOSettingsListDto } from '../models/SSOSettingsListDto';
import type { SSOSettingsResponseDto } from '../models/SSOSettingsResponseDto';
import type { UpdateSSOSettingsDto } from '../models/UpdateSSOSettingsDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class SsoSettingsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List
   * @returns SSOSettingsListDto Successful Response
   * @throws ApiError
   */
  public listApiV1SsosGet(): CancelablePromise<SSOSettingsListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ssos/',
    });
  }
  /**
   * Create Sso Settings
   * @returns SSOSettingsResponseDto Successful Response
   * @throws ApiError
   */
  public createSsoSettingsApiV1SsosPost({
    requestBody,
  }: {
    requestBody: CreateSSOSettingsDto,
  }): CancelablePromise<SSOSettingsResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/ssos/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Get Available Sso Providers
   * @returns any Successful Response
   * @throws ApiError
   */
  public getAvailableSsoProvidersApiV1SsosAvailableProvidersGet(): CancelablePromise<Array<any>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ssos/available-providers',
    });
  }
  /**
   * Get Sso Settings By Id
   * @returns ReadSSOSettingsDto Successful Response
   * @throws ApiError
   */
  public getSsoSettingsByIdApiV1SsosSsoIdGet({
    ssoId,
  }: {
    ssoId: string,
  }): CancelablePromise<ReadSSOSettingsDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ssos/{sso_id}',
      path: {
        'sso_id': ssoId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete Sso Settings
   * @returns boolean Successful Response
   * @throws ApiError
   */
  public deleteSsoSettingsApiV1SsosSsoIdDelete({
    ssoId,
  }: {
    ssoId: string,
  }): CancelablePromise<boolean> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/ssos/{sso_id}',
      path: {
        'sso_id': ssoId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Sso Settings
   * @returns void
   * @throws ApiError
   */
  public updateSsoSettingsApiV1SsosSsoIdPatch({
    ssoId,
    requestBody,
  }: {
    ssoId: string,
    requestBody: UpdateSSOSettingsDto,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/ssos/{sso_id}',
      path: {
        'sso_id': ssoId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
