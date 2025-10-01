/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AppConfigurationDto } from '../models/AppConfigurationDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AppConfigurationService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get App Configuration
   * @returns AppConfigurationDto Successful Response
   * @throws ApiError
   */
  public getAppConfigurationApiV1AppConfigurationGet(): CancelablePromise<AppConfigurationDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/app_configuration/',
    });
  }
}
