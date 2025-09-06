/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AIRequest } from '../models/AIRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AiService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
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
