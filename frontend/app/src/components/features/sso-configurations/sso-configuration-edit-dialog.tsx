import { ReadSSOSettingsDto } from '@/api';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {

    IconLoader2,

} from "@tabler/icons-react"
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { providerConfig, ssoFormSchema, SSOFormValues } from './sso-provider-configuration';
import { useSSOConfiguration } from '@/components/providers/sso-configuration-provider';
import { Switch } from '@/components/ui/switch';

interface SSOConfigurationEditDialogProps {
    editSSOProvider: ReadSSOSettingsDto | null;
    onClose?: () => void;
}
export default function SSOConfigurationEditDialog({ editSSOProvider, onClose }: SSOConfigurationEditDialogProps) {
    const {
        availableProviders,
        onUpdateSSOConfiguration

    } = useSSOConfiguration();

    const [loading, setLoading] = useState(false);
    const [editingProvider, setEditingProvider] =
        useState<ReadSSOSettingsDto | null>(editSSOProvider);

    const form = useForm<SSOFormValues>({
        resolver: zodResolver(ssoFormSchema) as any,
        defaultValues: {
            provider: editingProvider ? editingProvider.provider : 'google',
            client_id: editingProvider ? editingProvider.client_id : '',
            client_secret: editingProvider && editingProvider.client_secret || '',
            scopes: editingProvider && editingProvider.scopes?.join(', ') || '',
            enabled: editingProvider && editingProvider.enabled || false,
        },
    });

    function handleDialogClose() {
        form.reset();
        setEditingProvider(null);
        if (onClose) {
            onClose();
        }
    };

    async function handleUpdate(data: SSOFormValues) {
        if (!editingProvider) return;
        setLoading(true);
        const scopesArray = data.scopes
            ? data.scopes.split(',').map((s) => s.trim()).filter(Boolean)
            : [];
        const updateData = {
            provider: data.provider,
            client_id: data.client_id,
            client_secret: data.client_secret || null,
            scopes: scopesArray.length > 0 ? scopesArray : null,
            enabled: data.enabled,
        };
        await onUpdateSSOConfiguration(editingProvider.id, updateData);
        setLoading(false);
        handleDialogClose();
    }

    return (
        <Dialog open={editSSOProvider !== null} onOpenChange={handleDialogClose}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>
                        Edit SSO Provider
                    </DialogTitle>
                    <DialogDescription>
                        Configure OAuth 2.0 credentials for your SSO provider
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(handleUpdate)}
                        className="space-y-4"
                    >
                        <FormField
                            control={form.control}
                            name="provider"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Provider</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                        disabled={!!editingProvider}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select a provider" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            {availableProviders.map((provider) => (
                                                <SelectItem key={provider} value={provider}>
                                                    {providerConfig[provider]?.label || provider}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormDescription>
                                        Choose the OAuth provider you want to configure
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="client_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Client ID</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Enter client ID" {...field} />
                                    </FormControl>
                                    <FormDescription>
                                        OAuth 2.0 client ID from your provider
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="client_secret"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Client Secret (Optional)</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="password"
                                            placeholder="Enter client secret"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormDescription>
                                        OAuth 2.0 client secret (if required by provider)
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="scopes"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Scopes (Optional)</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="openid, profile, email"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormDescription>
                                        Comma-separated OAuth scopes (e.g., openid, profile,
                                        email)
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="enabled"
                            render={({ field }) => (
                                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                                    <div className="space-y-0.5">
                                        <FormLabel className="text-base">Enable Provider</FormLabel>
                                        <FormDescription>
                                            Allow users to sign in with this provider
                                        </FormDescription>
                                    </div>
                                    <FormControl>
                                        <Switch
                                            checked={field.value}
                                            onCheckedChange={field.onChange}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => handleDialogClose()}
                            >
                                Cancel
                            </Button>
                            <Button type="submit" disabled={loading}>
                                {loading && <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Update
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}