const pollingDelayInMilliSeconds = 10 * 1000 * 60;
setInterval(async () => {
    const url = "/api/v1/account/refresh";
    const response = await fetch(url, {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
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