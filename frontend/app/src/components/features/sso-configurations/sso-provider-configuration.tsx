import { useSSOConfiguration } from '@/components/providers/sso-configuration-provider';
import { Button } from '@/components/ui/button';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { Label } from '@/components/ui/label';


import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';

import { zodResolver } from '@hookform/resolvers/zod';

import {
    IconBrandGithub,
    IconBrandGoogle,
    IconBrandDiscord,
    IconBrandX,
    IconBrandLinkedin,
    IconBrandFacebook,
    IconBrandBitbucket,
    IconBrandGitlab,
    IconBrandNotion,
    IconBrandAzure,
    IconKey,
    IconTrash,
    IconBrandOauth,
    IconCircleCheck,
    IconAlertCircle,

} from "@tabler/icons-react"
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useState } from 'react';
import type { ReadSSOSettingsDto } from '@/api';
import DeleteSSOConfigurationDialog from './delete-sso-configuration-dialog';
import SSOConfigurationEditDialog from './sso-configuration-edit-dialog';
import CreateNewSSODialog from './create-new-sso-dialog';
import { cn } from '@/lib/utils';

const providerTypeEnum = [
    'google',
    'github',
    'discord',
    'microsoft',
    'linkedin',
    'x',
    'notion',
    'gitlab',
    'bitbucket',
    'facebook',
] as const
export const ssoFormSchema = z.object({
    provider: z.enum(providerTypeEnum),
    client_id: z.string().min(1, 'Client ID is required'),
    client_secret: z.string().default(''),
    scopes: z.string().default(''),
    enabled: z.boolean().default(true),
});

export type SSOFormValues = z.infer<typeof ssoFormSchema>;

// Provider display configuration
export const providerConfig: Record<
    string,
    { label: string; icon: typeof IconBrandGithub; color: string }
> = {
    google: { label: 'Google', icon: IconBrandGoogle, color: 'text-red-500' },
    github: { label: 'GitHub', icon: IconBrandGithub, color: 'text-gray-600' },
    discord: { label: 'Discord', icon: IconBrandDiscord, color: 'text-indigo-500' },
    microsoft: { label: 'Microsoft', icon: IconBrandAzure, color: 'text-blue-500' },
    linkedin: { label: 'LinkedIn', icon: IconBrandLinkedin, color: 'text-blue-600' },
    x: { label: 'X (Twitter)', icon: IconBrandX, color: 'text-gray-600' },
    notion: { label: 'Notion', icon: IconBrandNotion, color: 'text-gray-800' },
    gitlab: { label: 'GitLab', icon: IconBrandGitlab, color: 'text-orange-500' },
    bitbucket: { label: 'Bitbucket', icon: IconBrandBitbucket, color: 'text-blue-500' },
    facebook: { label: 'Facebook', icon: IconBrandFacebook, color: 'text-blue-600' },
};

export function SSOProviderConfiguration() {
    const {
        providers,
        availableProviders,
        onEnableOrDisableSSOLogin,
    } = useSSOConfiguration();

    const [providerToDelete, setProviderToDelete] =
        useState<ReadSSOSettingsDto | null>(null);
    const [editingProvider, setEditingProvider] =
        useState<ReadSSOSettingsDto | null>(null);

    const form = useForm<SSOFormValues>({
        resolver: zodResolver(ssoFormSchema) as any,
        defaultValues: {
            provider: 'google',
            client_id: '',
            client_secret: '',
            scopes: '',
            enabled: true,
        },
    });



    const handleEdit = (provider: ReadSSOSettingsDto) => {
        setEditingProvider(provider);
        form.reset({
            provider: provider.provider,
            client_id: provider.client_id,
            client_secret: provider.client_secret || '',
            scopes: provider.scopes ? provider.scopes.join(', ') : '',
            enabled: provider.enabled,
        });
    };

    const handleDelete = (provider: ReadSSOSettingsDto) => {
        setProviderToDelete(provider);
    };



    const handleToggleEnabled = async (provider: ReadSSOSettingsDto) => {
        await onEnableOrDisableSSOLogin(provider.id, !provider.enabled);

    };

    async function onUpdateProviderClose() {
        setEditingProvider(null)
    }

    return (
        <div className="space-y-6 ">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-medium">SSO Providers</h3>
                    <p className="text-sm text-muted-foreground">
                        Configure single sign-on providers for your application
                    </p>
                </div>
                {editingProvider && <SSOConfigurationEditDialog editSSOProvider={editingProvider} onClose={onUpdateProviderClose} />}
                <CreateNewSSODialog />
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Total Providers
                        </CardTitle>
                        <IconKey className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{providers.length}</div>
                        <p className="text-xs text-muted-foreground">
                            Configured SSO providers
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Active Providers
                        </CardTitle>
                        <IconCircleCheck className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {providers.filter((p) => p.enabled).length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Currently enabled for login
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Available Options
                        </CardTitle>
                        <IconBrandOauth className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{availableProviders.length}</div>
                        <p className="text-xs text-muted-foreground">
                            Supported providers
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Providers List */}
            {providers.length === 0 ? (
                <Card>
                    <CardContent className="flex flex-col items-center justify-center py-12">
                        <IconAlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
                        <p className="text-muted-foreground text-center">
                            No SSO providers configured yet.
                            <br />
                            Click "Add Provider" to get started.
                        </p>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {providers.map((provider) => {
                        const config = providerConfig[provider.provider] || {
                            label: provider.provider,
                            icon: IconBrandOauth,
                            color: 'text-gray-500',
                        };
                        const ProviderIcon = config.icon;

                        return (
                            <Card key={provider.id}>
                                <CardHeader>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <ProviderIcon className={cn('h-8 w-8', config.color)} />
                                            <div>
                                                <CardTitle className="text-base">
                                                    {config.label}
                                                </CardTitle>
                                                <CardDescription className="text-xs">
                                                    {provider.provider}
                                                </CardDescription>
                                            </div>
                                        </div>
                                        <Badge variant={provider.enabled ? 'default' : 'secondary'}>
                                            {provider.enabled ? 'Active' : 'Inactive'}
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="space-y-2">
                                        <div>
                                            <Label className="text-xs text-muted-foreground">
                                                Client ID
                                            </Label>
                                            <p className="text-sm font-mono truncate">
                                                {provider.client_id}
                                            </p>
                                        </div>
                                        {provider.scopes && provider.scopes.length > 0 && (
                                            <div>
                                                <Label className="text-xs text-muted-foreground">
                                                    Scopes
                                                </Label>
                                                <div className="flex flex-wrap gap-1 mt-1">
                                                    {provider.scopes.map((scope, idx) => (
                                                        <Badge key={idx} variant="outline" className="text-xs">
                                                            {scope}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    <div className="flex items-center justify-between pt-2 border-t">
                                        <div className="flex items-center space-x-2">
                                            <Switch
                                                checked={provider.enabled}
                                                onCheckedChange={() => handleToggleEnabled(provider)}
                                            />
                                            <Label className="text-sm">Enable</Label>
                                        </div>
                                        <div className="flex space-x-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => handleEdit(provider)}
                                            >
                                                Edit
                                            </Button>
                                            <Button
                                                variant="destructive"
                                                size="sm"
                                                onClick={() => handleDelete(provider)}
                                            >
                                                <IconTrash className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            )}

            {providerToDelete && (
                <DeleteSSOConfigurationDialog deleteSSOProviderId={providerToDelete.id} />
            )}

        </div>
    );
}