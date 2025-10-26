/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateProductDto } from '../models/CreateProductDto';
import type { ProductListDto } from '../models/ProductListDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StripeProductsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List Products
   * @returns ProductListDto Successful Response
   * @throws ApiError
   */
  public listProductsApiV1ProductsGet({
    active = true,
  }: {
    /**
     * Filter active products, defaults to True
     */
    active?: boolean,
  }): CancelablePromise<ProductListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/products/',
      query: {
        'active': active,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create a Product
   * @returns any Successful Response
   * @throws ApiError
   */
  public createProductApiV1ProductsCreatePost({
    requestBody,
  }: {
    requestBody: CreateProductDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/products/create',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update a Product
   * @returns void
   * @throws ApiError
   */
  public updateProductApiV1ProductsProductIdUpdatePatch({
    productId,
    requestBody,
  }: {
    productId: string,
    requestBody: CreateProductDto,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/products/{product_id}/update',
      path: {
        'product_id': productId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete a Product
   * @returns any Successful Response
   * @throws ApiError
   */
  public deleteProductApiV1ProductsProductIdDeleteDelete({
    productId,
  }: {
    productId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/products/{product_id}/delete',
      path: {
        'product_id': productId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
