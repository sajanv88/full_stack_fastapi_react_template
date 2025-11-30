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

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {

    IconLoader2,

} from "@tabler/icons-react"
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ssoFormSchema, SSOFormValues } from './sso-provider-configuration';
import { useSSOConfiguration } from '@/components/providers/sso-configuration-provider';
import { Switch } from '@/components/ui/switch';

interface SSOConfigurationEditDialogProps {
    editSSOProvider: ReadSSOSettingsDto;
    onClose?: () => void;
}
export default function SSOConfigurationEditDialog({ editSSOProvider, onClose }: SSOConfigurationEditDialogProps) {
    const {
        onUpdateSSOConfiguration

    } = useSSOConfiguration();

    const [loading, setLoading] = useState(false);


    const form = useForm<SSOFormValues>({
        resolver: zodResolver(ssoFormSchema) as any,
        defaultValues: {
            provider: editSSOProvider.provider,
            client_id: editSSOProvider.client_id,
            client_secret: '',
            scopes: editSSOProvider.scopes?.join(', ') || '',
            enabled: editSSOProvider.enabled || false,
        },
    });

    function handleDialogClose() {
        form.reset();
        if (onClose) {
            onClose();
        }
    };

    async function handleUpdate(data: SSOFormValues) {
        if (!editSSOProvider) return;
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
        await onUpdateSSOConfiguration(editSSOProvider.id, updateData);
        setLoading(false);
        handleDialogClose();
    }




    return (
        <Dialog open={editSSOProvider !== null} onOpenChange={handleDialogClose}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle className='capitalize'>
                        Update {editSSOProvider.provider}
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