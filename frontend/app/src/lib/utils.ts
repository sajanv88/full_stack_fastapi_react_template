import { ApiClient, type Tenant, type TokenSet } from "@/api"
import { clsx, type ClassValue } from "clsx"
import { toast } from "sonner";
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


export function setTenant(tenant: Tenant | null) {
  if (!tenant) {
    localStorage.removeItem("_tenant");
    return;
  }
  localStorage.setItem("_tenant", JSON.stringify(tenant));
}

export function getTenant(): Tenant | null {
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
  if (!refreshTokenExpiresAt) {
    console.error("No refresh token expiry available");
    return;
  }
  const expiry = Date.now() + (Number(refreshTokenExpiresAt) * 1000); // Convert to milliseconds
  console.log("Refresh token expiry (ms):", expiry);

  const refreshTime = expiry - Date.now() - (5 * 60 * 1000); // refresh 5 mins early
  console.log("Scheduling token refresh in (ms):", refreshTime);

  if (refreshTime <= 0) {
    console.log("⏰ Refreshing immediately...");
    cb();
  } else {
    setTimeout(async () => {
      console.log("⏰ Refreshing token...");
      await cb();
    }, refreshTime);
  }

}

export function userProfileImageUrl(url: string | null | undefined) {
  if (!url) return "https://github.com/evilrabbit.png";
  return url;
}


export function getApiClient() {
  const accessToken = getAccessToken();
  const tenant = getTenant();
  if (!accessToken) {
    if (tenant) {
      return new ApiClient({
        HEADERS: {
          "X-Tenant-ID": tenant.id
        }
      })
    }
    return new ApiClient();
  }
  return new ApiClient({
    HEADERS: {
      Authorization: `Bearer ${accessToken}`,
      ...tenant?.id && { "X-Tenant-ID": tenant.id }
    }
  });
}


export async function getAIChatNewSession() {
  try {
    const apiClient = getApiClient();
    const response = await apiClient.ai.createNewSessionApiV1AiNewSessionGet();
    return response.session_id;
  } catch (error) {
    console.error("Failed to create new AI session:", error);
    toast.error("Failed to create new AI session", { richColors: true, position: "top-center" });
    throw new Error("Failed to create new AI session");
  }
}