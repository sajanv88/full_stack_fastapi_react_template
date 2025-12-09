import { useBrandingContext } from "@/components/providers/branding-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    IconSettingsStar,
    IconPalette,
    IconPhone,
    IconMail,
    IconMapPin,
    IconLoader2,
    IconCheck,
    IconIdBadge2
} from "@tabler/icons-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { useState } from "react";
import type { UpdateBrandingDto } from "@/api";

const contactInfoSchema = z.object({
    support_email: z.string().email('Invalid email').optional().or(z.literal('')),
    phone: z.string().optional(),
    address: z.string().optional(),
});

const themeColorsSchema = z.object({
    background: z.string().optional(),
    foreground: z.string().optional(),
    primary: z.string().optional(),
    primary_foreground: z.string().optional(),
    secondary: z.string().optional(),
    secondary_foreground: z.string().optional(),
    muted: z.string().optional(),
    muted_foreground: z.string().optional(),
    accent: z.string().optional(),
    accent_foreground: z.string().optional(),
    destructive: z.string().optional(),
    destructive_foreground: z.string().optional(),
    border: z.string().optional(),
    input: z.string().optional(),
    ring: z.string().optional(),
    card: z.string().optional(),
    card_foreground: z.string().optional(),
});

const brandingFormSchema = z.object({
    contact_info: contactInfoSchema.optional(),
    theme_config: z.object({
        radius: z.string().optional(),
        light: themeColorsSchema.optional(),
        dark: themeColorsSchema.optional(),
    }).optional(),
});

type BrandingFormValues = z.infer<typeof brandingFormSchema>;

export default function BrandingConfiguration() {
    const { branding, onUpdateBranding } = useBrandingContext();
    const [loading, setLoading] = useState(false);
    const [saved, setSaved] = useState(false);

    const form = useForm<BrandingFormValues>({
        resolver: zodResolver(brandingFormSchema),
        defaultValues: {
            contact_info: {
                support_email: branding?.contact_info?.support_email || '',
                phone: branding?.contact_info?.phone || '',
                address: branding?.contact_info?.address || '',
            },
            theme_config: {
                radius: branding?.theme_config?.radius || '0.5rem',
                light: branding?.theme_config?.light || {},
                dark: branding?.theme_config?.dark || {},
            },
        },
    });

    const onSubmit = async (data: BrandingFormValues) => {
        setLoading(true);
        setSaved(false);
        try {
            const updateData: UpdateBrandingDto = {
                contact_info: data.contact_info || null,
                theme_config: data.theme_config || null,
            };
            await onUpdateBranding(updateData);
            setSaved(true);
            setTimeout(() => setSaved(false), 2000);
        } catch (error) {
            console.error('Failed to update branding:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card className="mt-6">
            <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                    <IconSettingsStar className="w-5 h-5" />
                    <span>Brand Configuration</span>
                </CardTitle>
                <CardDescription>
                    Customize your application's appearance and contact information
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                        <Tabs defaultValue="identity" className="w-full">
                            <TabsList className="grid w-full grid-cols-3">
                                <TabsTrigger value="identity">
                                    <IconIdBadge2 className="w-4 h-4 mr-2" />
                                    Identity
                                </TabsTrigger>
                                <TabsTrigger value="contact">
                                    <IconPhone className="w-4 h-4 mr-2" />
                                    Contact Info
                                </TabsTrigger>
                                <TabsTrigger value="theme">
                                    <IconPalette className="w-4 h-4 mr-2" />
                                    Theme Colors
                                </TabsTrigger>
                            </TabsList>
                            <TabsContent value="identity" className="space-y-4 pt-5">
                                <div className="space-y-4">
                                    <h1>Upload logo</h1>
                                </div>
                            </TabsContent>
                            {/* Contact Information Tab */}
                            <TabsContent value="contact" className="space-y-4 pt-5">
                                <div className="space-y-4">
                                    <FormField
                                        control={form.control}
                                        name="contact_info.support_email"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="flex items-center space-x-2">
                                                    <IconMail className="w-4 h-4" />
                                                    <span>Support Email</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input
                                                        type="email"
                                                        placeholder="support@example.com"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Primary contact email for customer support
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <FormField
                                        control={form.control}
                                        name="contact_info.phone"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="flex items-center space-x-2">
                                                    <IconPhone className="w-4 h-4" />
                                                    <span>Phone Number</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="+1 (555) 123-4567"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Contact phone number
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <FormField
                                        control={form.control}
                                        name="contact_info.address"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="flex items-center space-x-2">
                                                    <IconMapPin className="w-4 h-4" />
                                                    <span>Address</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="123 Main St, City, State ZIP"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Business address
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                </div>
                            </TabsContent>

                            {/* Theme Configuration Tab */}
                            <TabsContent value="theme" className="space-y-4 pt-5">
                                <div className="space-y-6">
                                    <FormField
                                        control={form.control}
                                        name="theme_config.radius"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Border Radius</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="0.5rem"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Global border radius (e.g., 0.5rem, 8px)
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <Separator />

                                    {/* Light Mode Colors */}
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-medium">Light Mode</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.background"
                                                label="Background"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.foreground"
                                                label="Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.primary"
                                                label="Primary"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.primary_foreground"
                                                label="Primary Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.secondary"
                                                label="Secondary"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.secondary_foreground"
                                                label="Secondary Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.accent"
                                                label="Accent"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.accent_foreground"
                                                label="Accent Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.border"
                                                label="Border"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.light.ring"
                                                label="Ring"
                                            />
                                        </div>
                                    </div>

                                    <Separator />

                                    {/* Dark Mode Colors */}
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-medium">Dark Mode</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.background"
                                                label="Background"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.foreground"
                                                label="Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.primary"
                                                label="Primary"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.primary_foreground"
                                                label="Primary Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.secondary"
                                                label="Secondary"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.secondary_foreground"
                                                label="Secondary Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.accent"
                                                label="Accent"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.accent_foreground"
                                                label="Accent Foreground"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.border"
                                                label="Border"
                                            />
                                            <ColorField
                                                control={form.control}
                                                name="theme_config.dark.ring"
                                                label="Ring"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </TabsContent>
                        </Tabs>

                        <div className="flex justify-end">
                            <Button type="submit" disabled={loading}>
                                {loading ? (
                                    <>
                                        <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Saving...
                                    </>
                                ) : saved ? (
                                    <>
                                        <IconCheck className="mr-2 h-4 w-4" />
                                        Saved
                                    </>
                                ) : (
                                    'Save Changes'
                                )}
                            </Button>
                        </div>
                    </form>
                </Form>
            </CardContent>
        </Card>
    );
}

// Helper component for color fields
function ColorField({
    control,
    name,
    label
}: {
    control: any;
    name: any;
    label: string;
}) {
    return (
        <FormField
            control={control}
            name={name}
            render={({ field }) => (
                <FormItem>
                    <FormLabel className="text-sm">{label}</FormLabel>
                    <FormControl>
                        <div className="flex items-center space-x-2">
                            <Input
                                placeholder="HSL value (e.g., 0 0% 100%)"
                                {...field}
                                className="flex-1"
                            />
                            {field.value && (
                                <div
                                    className="w-10 h-10 rounded border"
                                    style={{
                                        background: `hsl(${field.value})`
                                    }}
                                />
                            )}
                        </div>
                    </FormControl>
                    <FormMessage />
                </FormItem>
            )}
        />
    );
}