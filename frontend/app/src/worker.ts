const pollingDelayInMilliSeconds = 10 * 1000 * 60;
let tenantId: string | null = null;

self.addEventListener("message", (event: MessageEvent<{ tenantId: string }>) => {
    if (event.data && event.data.tenantId) {
        console.log("Worker received tenantId:", event.data.tenantId);
        tenantId = event.data.tenantId;
    } else if (event.data && event.data.tenantId === null) {
        console.log("Worker received tenantId removal");
        tenantId = null;
    }
});
setInterval(async () => {
    const url = "/api/v1/account/refresh";
    console.log("Worker fetching new token with tenantId:", tenantId);
    const response = await fetch(url, {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...(tenantId && { "X-Tenant-ID": tenantId }),
        },
    });
    const data = await response.json();
    const unauthorizedMessage = {
        message: "Unauthorized",
        code: response.status,
    };
    if (!response.ok || response.status === 401) {
        return self.postMessage(unauthorizedMessage);
    }
    self.postMessage(data);
}, pollingDelayInMilliSeconds);