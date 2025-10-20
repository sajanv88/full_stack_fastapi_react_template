/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Feature } from '../models/Feature';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class FeaturesService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List Features
   * List all available features. Requires HOST_MANAGE_TENANTS permission.
   * @returns Feature Successful Response
   * @throws ApiError
   */
  public listFeaturesApiV1FeaturesGet(): CancelablePromise<Array<Feature>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/features/',
    });
  }
}
