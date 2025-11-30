import { useAppConfig } from "@/components/providers/app-config-provider";
import { providerConfig } from "@/components/features/sso-configurations/sso-provider-configuration";
import { Button } from "@/components/ui/button";
import { IconBrandAuth0 } from "@tabler/icons-react";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

export function SSOLoginDialog() {
    const { enabled_sso_providers } = useAppConfig()

    function renderIcon(provider: typeof providerConfig[keyof typeof providerConfig]) {
        const IconComponent = provider.icon;
        return <IconComponent className={cn('h-8 w-8', provider.color)} />
    }
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
                <DialogContent className="max-w-sm">
                    <div className="text-lg font-medium mb-4">Single Sign-On (SSO) Login</div>
                    <div className="grid sm:grid-cols-2 gap-4">
                        {enabled_sso_providers.map((provider) => (
                            <a href={`/api/v1/account/sso/${provider}/login`} className="flex items-center space-x-2 bg-primary/90 dark:bg-primary p-1 text-primary-foreground justify-center rounded-2xl dark:hover:bg-primary/90 hover:bg-primary/80 transition-all">
                                {renderIcon(providerConfig[provider])}
                                <span className="capitalize text-md">Continue with {provider}</span>
                            </a>

                        ))}
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    )
}