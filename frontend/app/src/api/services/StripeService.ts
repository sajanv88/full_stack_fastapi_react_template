/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateStripeSettingDto } from '../models/CreateStripeSettingDto';
import type { StripeSettingDto } from '../models/StripeSettingDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StripeService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Stripe Settings
   * @returns StripeSettingDto Successful Response
   * @throws ApiError
   */
  public getStripeSettingsApiV1ConfigurationsStripeGet(): CancelablePromise<StripeSettingDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/configurations/stripe',
    });
  }
  /**
   * Configure Stripe Setting
   * @returns any Successful Response
   * @throws ApiError
   */
  public configureStripeSettingApiV1ConfigurationsStripePost({
    requestBody,
  }: {
    requestBody: CreateStripeSettingDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/configurations/stripe',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Stripe Webhook
   * @returns any Successful Response
   * @throws ApiError
   */
  public stripeWebhookApiV1ConfigurationsStripeWebhooksPost(): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/configurations/stripe/webhooks',
    });
  }
}
