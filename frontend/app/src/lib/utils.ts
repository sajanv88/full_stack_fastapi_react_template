import type { TokenSet } from "@/api"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


export function storeTokenSet(tokenSet: TokenSet) {
  sessionStorage.setItem("access_token", tokenSet.access_token);
  localStorage.setItem("refresh_token", tokenSet.refresh_token);
  localStorage.setItem("refresh_token_expires_at", tokenSet.refresh_token_expires_in?.toString() || "");
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
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("refresh_token_expires_at");
}


export function scheduleTokenRefresh(cb: () => Promise<void>) {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    console.error("No refresh token available");
    return;
  }

  const refreshTokenExpiresAt = localStorage.getItem("refresh_token_expires_at");
  if (!refreshTokenExpiresAt) {
    console.error("No refresh token expiry available");
    return;
  }
  const expiry = parseInt(refreshTokenExpiresAt) * 1000; // exp is in seconds, convert to ms

  const refreshTime = expiry - Date.now() - (5 * 60 * 1000);
  if (refreshTime > 0) {
    setTimeout(async () => {
      console.log("⏰ Refreshing token...");
      await cb();
    }, refreshTime);
  }

}

export function userProfileImageUrl(url: string | null | undefined) {
  if (!url) return "https://github.com/evilrabbit.png";
  return url.replace("app/ui", "");
}