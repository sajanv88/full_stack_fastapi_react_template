import type { TokenSet } from "@/api"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


export function storeTokenSet(tokenSet: TokenSet) {
  sessionStorage.setItem("access_token", tokenSet.access_token);
  localStorage.setItem("refresh_token", tokenSet.refresh_token);
  sessionStorage.setItem("logged_in", "true");

}

export function getAccessToken() {
  return sessionStorage.getItem("access_token");
}

export function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

export function isLoggedIn() {
  return sessionStorage.getItem("logged_in") === "true";
}

export function clearIsLoggedIn() {
  sessionStorage.setItem("logged_in", "false");
}

export function clearAllTokens() {
  sessionStorage.clear();
  localStorage.clear();
}
