import { useAppConfig } from "@/components/providers/app-config-provider";
import { providerConfig } from "@/components/features/sso-configurations/sso-provider-configuration";
import React from "react";
import { Button } from "@/components/ui/button";
import { IconBrandAuth0 } from "@tabler/icons-react";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";

export function SSOLoginDialog() {
    const { enabled_sso_providers } = useAppConfig()
    if (!enabled_sso_providers || enabled_sso_providers.length === 0) {
        return null
    }
    return (
        <div className="mt-6">
            <Dialog>
                <DialogTrigger asChild>
                    <Button className="w-full" variant="outline" >
                        <IconBrandAuth0 className="w-4 h-4 mr-2" />
                        Login with SSO
                    </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-sm">
                    <div className="text-lg font-medium mb-4">Single Sign-On (SSO) Login</div>
                    <div className="flex flex-col gap-3">
                        {enabled_sso_providers.map((provider) => (
                            <Button
                                asChild
                                key={provider}
                                variant="link"
                                size="lg"

                            >
                                <a href={`/api/v1/account/sso/${provider}/login`} className="text-2xl">
                                    {providerConfig[provider]?.icon && React.createElement(providerConfig[provider].icon, { className: "w-10 h-10" })}
                                    Continue with {provider}
                                </a>
                            </Button>
                        ))}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    )
}