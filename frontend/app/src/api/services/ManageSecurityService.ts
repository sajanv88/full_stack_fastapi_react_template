/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RegisteredPasskeyCredentialsDto } from '../models/RegisteredPasskeyCredentialsDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ManageSecurityService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Registered Passkeys
   * Endpoint to retrieve registered passkeys for the current user.
   * @returns RegisteredPasskeyCredentialsDto Successful Response
   * @throws ApiError
   */
  public getRegisteredPasskeysApiV1SecurityPasskeysGet(): CancelablePromise<Array<RegisteredPasskeyCredentialsDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/security/passkeys',
    });
  }
  /**
   * Delete Registered Passkey
   * Endpoint to delete a registered passkey for the current user.
   * @returns void
   * @throws ApiError
   */
  public deleteRegisteredPasskeyApiV1SecurityPasskeysCredentialIdDelete({
    credentialId,
  }: {
    credentialId: string,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/security/passkeys/{credential_id}',
      path: {
        'credential_id': credentialId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
