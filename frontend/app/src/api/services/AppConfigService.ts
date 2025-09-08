/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AppConfigResponse } from '../models/AppConfigResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AppConfigService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get App Config
   * @returns AppConfigResponse Successful Response
   * @throws ApiError
   */
  public getAppConfigApiV1ConfigGet(): CancelablePromise<AppConfigResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/config/',
    });
  }
}
