import { ApiClient, type TenantDto, type TokenSetDto } from "@/api"
import { clsx, type ClassValue } from "clsx"
import { toast } from "sonner";
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


export function storeTokenSet(tokenSet: TokenSetDto) {
  sessionStorage.setItem("access_token", tokenSet.access_token);
  sessionStorage.setItem("access_token_expires_at", tokenSet.expires_in?.toString() || "");
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


export function setTenant(tenant: TenantDto | null) {
  if (!tenant) {
    localStorage.removeItem("_tenant");
    return;
  }
  localStorage.setItem("_tenant", JSON.stringify(tenant));
}

export function getTenant(): TenantDto | null {
  const tenant = localStorage.getItem("_tenant");
  return tenant ? JSON.parse(tenant) : null;
}

export function scheduleTokenRefresh(cb: () => Promise<void>) {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    console.error("No refresh token available");
    return;
  }

  const refreshTokenExpiresAt = localStorage.getItem("refresh_token_expires_at");
  const accessTokenExpiresIn = sessionStorage.getItem("access_token_expires_at");
  if (!refreshTokenExpiresAt) {
    console.error("No refresh token expiry available");
    return;
  }
  const expiry = Number(accessTokenExpiresIn) * 1000; // Convert to milliseconds

  const refreshTime = expiry - Date.now() - (10 * 60 * 1000); // refresh 10 mins early

  if (refreshTime <= 0 || expiry - Date.now() <= 0) {
    console.error("Refresh time is in the past, cannot schedule token refresh");
    cb();
    return;
  }
  setTimeout(() => {
    cb().catch(err => console.error("Token refresh failed", err));
  }, refreshTime);
}

export function userProfileImageUrl(url: string | null | undefined) {
  if (!url) return "https://github.com/evilrabbit.png";
  return url;
}


export function getApiClient(accessToken?: string) {
  // console.log("Getting API client with access token:", accessToken);
  const tenant = getTenant();
  if (!accessToken) {
    if (tenant) {
      return new ApiClient({
        HEADERS: {
          "X-Tenant-ID": tenant.id!
        },
        WITH_CREDENTIALS: true,
      })
    }
    return new ApiClient({
      WITH_CREDENTIALS: true,
    });
  }
  return new ApiClient({
    HEADERS: {
      Authorization: `Bearer ${accessToken}`,
      ...tenant?.id && { "X-Tenant-ID": tenant.id }
    },
    WITH_CREDENTIALS: true
  });
}


