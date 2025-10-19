import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import {
    Fingerprint,
    Shield,
    Mail
} from "lucide-react";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { getApiClient } from "@/lib/utils";
import { startRegistration, startAuthentication, WebAuthnError } from "@simplewebauthn/browser";
import { useNavigate } from "react-router";
import { useAuthContext } from "@/components/providers/auth-provider";


const passkeyEmailSchema = z.object({
    email: z.email({ message: "Please enter a valid email address" })
});

type PasskeyEmailForm = z.infer<typeof passkeyEmailSchema>;


export function PasskeyLogin() {
    const navigate = useNavigate();
    const { refreshCurrentUser } = useAuthContext();
    const [isLoading, setIsLoading] = useState(false);
    const [showEmailDialog, setShowEmailDialog] = useState(false);

    const form = useForm<PasskeyEmailForm>({
        resolver: zodResolver(passkeyEmailSchema),
        defaultValues: {
            email: ""
        }
    });

    const handlePasskeyClick = () => {
        setShowEmailDialog(true);
    };


    async function loginFlow(email: string) {
        const apiClient = getApiClient();
        const loginOpts = await apiClient.account.passkeyLoginOptionsApiV1AccountPasskeyLoginOptionsPost({
            requestBody: email
        })
        const loginOptsRes = JSON.parse(loginOpts);
        const authResp = await startAuthentication(loginOptsRes);
        await apiClient.account.passkeyLoginApiV1AccountPasskeyLoginPost({
            requestBody: {
                credential: authResp,
                email: email
            }
        })
        await refreshCurrentUser();
        navigate("/dashboard");
    }


    async function registerFlow(email: string) {
        const apiClient = getApiClient();

        const regOpts = await apiClient
            .account.passkeyRegisterOptionsApiV1AccountPasskeyRegisterOptionsPost({
                requestBody: email
            })
        const regOptsRes = JSON.parse(regOpts)
        const attResp = await startRegistration(regOptsRes);
        await apiClient.account.passkeyRegisterApiV1AccountPasskeyRegisterPost({
            requestBody: {
                credential: attResp,
                email: email
            }
        })
        toast.success("Passkey registered successfully!", {
            description: "You can now use your passkey for future logins.",
            richColors: true
        });
    }
    const handleEmailSubmit = async (data: PasskeyEmailForm) => {
        setIsLoading(true);
        const apiClient = getApiClient();
        try {
            const res = await apiClient.account.hasPasskeysApiV1AccountPasskeyHasPasskeysPost({
                requestBody: data.email
            });
            console.log({ res }, "Passkey Support Check");
            if (res.has_passkeys) {
                await loginFlow(data.email);
                return;
            }
            await registerFlow(data.email);
            setShowEmailDialog(false);
            form.reset();
            toast.success("Passkey authentication successful!");

        } catch (error) {
            if (error instanceof WebAuthnError) {
                toast.error("Sorry!", {
                    description: error.message,
                    richColors: true,
                    position: "top-right"
                });
                return;
            }

            console.error("Passkey error:", error);
            toast.error("Passkey authentication failed. Please ensure you have a registered passkey.", {
                richColors: true,
                position: "top-right"
            });

        }
        finally {
            setShowEmailDialog(false);
            setIsLoading(false);

        }



    };

    const handleDialogClose = () => {
        if (!isLoading) {
            setShowEmailDialog(false);
            form.reset();
        }
    };



    return (
        <div>
            {/* Passkey Authentication */}
            <Card className="border-2 border-dashed border-primary/20 hover:border-primary/40 transition-colors">
                <CardContent className="p-4">
                    <Button
                        variant="outline"
                        className="w-full h-12 text-left justify-start gap-3 border-none hover:bg-primary/5"
                        onClick={handlePasskeyClick}
                        disabled={isLoading}
                    >
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10">
                            <Fingerprint className="w-4 h-4 text-primary" />
                        </div>
                        <div className="flex-1">
                            <div className="font-medium">Sign in with Passkey</div>
                            <div className="text-xs text-muted-foreground">
                                Use your biometric or device authentication
                            </div>
                        </div>
                        <Shield className="w-4 h-4 text-green-500" />
                    </Button>
                </CardContent>
            </Card>



            {/* Email Dialog for Passkey */}
            <Dialog open={showEmailDialog} onOpenChange={handleDialogClose}>
                <DialogContent className="sm:max-w-md" isFullBlack>
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <Fingerprint className="w-5 h-5 text-primary" />
                            Passkey Authentication
                        </DialogTitle>
                        <DialogDescription>
                            Enter your email address to authenticate with your passkey
                        </DialogDescription>
                    </DialogHeader>

                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(handleEmailSubmit)} className="space-y-4">
                            <FormField
                                control={form.control}
                                name="email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Email Address</FormLabel>
                                        <FormControl>
                                            <div className="relative">
                                                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                                                <Input
                                                    placeholder="Enter your email"
                                                    className="pl-10"
                                                    disabled={isLoading}
                                                    {...field}
                                                />
                                            </div>
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <DialogFooter className="flex gap-2">
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={handleDialogClose}
                                    disabled={isLoading}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    disabled={isLoading}
                                    className="flex items-center gap-2"
                                >
                                    {isLoading ? (
                                        <>
                                            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                            Authenticating...
                                        </>
                                    ) : (
                                        <>
                                            <Shield className="w-4 h-4" />
                                            Authenticate
                                        </>
                                    )}
                                </Button>
                            </DialogFooter>
                        </form>
                    </Form>
                </DialogContent>
            </Dialog>
        </div>
    );
}