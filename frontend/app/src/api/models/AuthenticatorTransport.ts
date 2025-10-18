/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * How an authenticator communicates to the client/browser.
 *
 * Members:
 * `USB`: USB wired connection
 * `NFC`: Near Field Communication
 * `BLE`: Bluetooth Low Energy
 * `INTERNAL`: Direct connection (read: a platform authenticator)
 * `CABLE`: Cloud Assisted Bluetooth Low Energy
 * `HYBRID`: A combination of (often separate) data-transport and proximity mechanisms
 *
 * https://www.w3.org/TR/webauthn-2/#enum-transport
 */
export type AuthenticatorTransport = 'usb' | 'nfc' | 'ble' | 'smart-card' | 'internal' | 'cable' | 'hybrid';
