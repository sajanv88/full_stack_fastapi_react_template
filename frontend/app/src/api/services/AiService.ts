/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AIRequest } from '../models/AIRequest';
import type { ModelsResponse } from '../models/ModelsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AiService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Models
   * @returns ModelsResponse Successful Response
   * @throws ApiError
   */
  public getModelsApiV1AiModelsGet(): CancelablePromise<Array<ModelsResponse>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/models',
    });
  }
  /**
   * Ask Ai
   * @returns any Successful Response
   * @throws ApiError
   */
  public askAiApiV1AiAskPost({
    requestBody,
  }: {
    requestBody: AIRequest,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/ai/ask',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
