import { useState } from "react";

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
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
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { providerConfig, ssoFormSchema, SSOFormValues } from './sso-provider-configuration';
import { useSSOConfiguration } from '@/components/providers/sso-configuration-provider';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import {

    IconPlus,
    IconLoader2,

} from "@tabler/icons-react"

export default function CreateNewSSODialog() {
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const {
        availableProviders,
        onCreateSSOConfiguration,
    } = useSSOConfiguration();

    const form = useForm<SSOFormValues>({
        resolver: zodResolver(ssoFormSchema) as any,
        defaultValues: {
            provider: undefined,
            client_id: '',
            client_secret: '',
            scopes: '',
            enabled: false,
        },
    });
    async function handleCreateOrUpdate(data: SSOFormValues) {
        setLoading(true);
        const scopesArray = data.scopes
            ? data.scopes.split(',').map((s) => s.trim()).filter(Boolean)
            : [];


        // Create new provider
        await onCreateSSOConfiguration({
            provider: data.provider,
            client_id: data.client_id,
            client_secret: data.client_secret || null,
            scopes: scopesArray.length > 0 ? scopesArray : null,
            enabled: data.enabled,
        });

        form.reset();
        setLoading(false);
        handleDialogClose(false);

    };

    function handleDialogClose(flag: boolean) {
        form.reset();
        setOpen(flag);
    };

    return (
        <Dialog open={open} onOpenChange={handleDialogClose}>
            <DialogTrigger asChild>
                <>
                    <Button onClick={() => setOpen(true)} className="hidden sm:flex">
                        <IconPlus className="mr-2 h-4 w-4" />
                        Add New SSO Provider
                    </Button>
                    <Button onClick={() => setOpen(true)} className="flex sm:hidden p-2">
                        <IconPlus className="h-4 w-4" />
                    </Button>
                </>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>
                        Configure SSO Provider
                    </DialogTitle>
                    <DialogDescription>
                        Configure OAuth 2.0 credentials for your SSO provider
                    </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(handleCreateOrUpdate)}
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
                                onClick={() => handleDialogClose(false)}
                            >
                                Cancel
                            </Button>
                            <Button type="submit" disabled={loading}>
                                {loading && <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />}
                                Create
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}