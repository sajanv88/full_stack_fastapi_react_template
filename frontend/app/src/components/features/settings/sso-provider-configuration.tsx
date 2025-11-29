import SSOConfigurationProvider from "@/components/providers/sso-configuration-provider";

export function SSOProviderConfiguration() {
    return (
        <SSOConfigurationProvider>
            <div>
                <h1>SSO Provider Configuration</h1>
            </div>
        </SSOConfigurationProvider>
    );
}