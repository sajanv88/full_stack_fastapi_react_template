/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BillingRecordListDto } from '../models/BillingRecordListDto';
import type { CheckoutRequestDto } from '../models/CheckoutRequestDto';
import type { CheckoutResponseDto } from '../models/CheckoutResponseDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StripeCheckoutService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Create Host Checkout Session
   * @returns CheckoutResponseDto Successful Response
   * @throws ApiError
   */
  public createHostCheckoutSessionApiV1CheckoutsHostTenantIdTenantPost({
    requestBody,
  }: {
    requestBody: CheckoutRequestDto,
  }): CancelablePromise<CheckoutResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/checkouts/host/{tenant_id}/tenant',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create Tenant Checkout Session
   * @returns CheckoutResponseDto Successful Response
   * @throws ApiError
   */
  public createTenantCheckoutSessionApiV1CheckoutsTenantSubscriptionPost({
    requestBody,
  }: {
    requestBody: CheckoutRequestDto,
  }): CancelablePromise<CheckoutResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/checkouts/tenant/subscription',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Host Checkout Success
   * @returns any Successful Response
   * @throws ApiError
   */
  public hostCheckoutSuccessApiV1CheckoutsHostPaymentSuccessPost({
    sessionId,
    tenantId,
  }: {
    sessionId: string,
    tenantId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/checkouts/host/payment/success',
      query: {
        'session_id': sessionId,
        'tenant_id': tenantId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Host Checkout Success
   * @returns any Successful Response
   * @throws ApiError
   */
  public hostCheckoutSuccessApiV1CheckoutsHostPaymentCancelPost({
    tenantId,
  }: {
    tenantId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/checkouts/host/payment/cancel',
      query: {
        'tenant_id': tenantId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Tenant Checkout Success
   * @returns any Successful Response
   * @throws ApiError
   */
  public tenantCheckoutSuccessApiV1CheckoutsTenantPaymentSuccessPost({
    sessionId,
  }: {
    sessionId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/checkouts/tenant/payment/success',
      query: {
        'session_id': sessionId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Tenant Checkout Canceled
   * @returns any Successful Response
   * @throws ApiError
   */
  public tenantCheckoutCanceledApiV1CheckoutsTenantPaymentCancelPost(): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/checkouts/tenant/payment/cancel',
    });
  }
  /**
   * List Checkout Records
   * @returns BillingRecordListDto Successful Response
   * @throws ApiError
   */
  public listCheckoutRecordsApiV1CheckoutsAllGet({
    skip,
    limit = 100,
  }: {
    skip?: number,
    limit?: number,
  }): CancelablePromise<BillingRecordListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/checkouts/all',
      query: {
        'skip': skip,
        'limit': limit,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
