/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InvoiceListDto } from '../models/InvoiceListDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StripeInvoicesService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List invoices
   * @returns InvoiceListDto Successful Response
   * @throws ApiError
   */
  public listInvoicesApiV1InvoicesGet(): CancelablePromise<InvoiceListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/invoices/',
    });
  }
}
