import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    Form,
    FormField,
    FormItem,
    FormLabel,
    FormControl,
    FormMessage,
    FormDescription
} from "@/components/ui/form";
import { toast } from "sonner";
import { Mail, Send, CheckCircle, ArrowLeft } from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { getApiClient } from "@/lib/utils";

const magicLinkSchema = z.object({
    email: z.string().email({ message: "Please enter a valid email address" })
});

type MagicLinkFormData = z.infer<typeof magicLinkSchema>;

export function MagicLinkLogin() {
    const [isLoading, setIsLoading] = useState(false);
    const [emailSent, setEmailSent] = useState(false);
    const [sentToEmail, setSentToEmail] = useState("");
    const [showEmailDialog, setShowEmailDialog] = useState(false);

    const form = useForm<MagicLinkFormData>({
        resolver: zodResolver(magicLinkSchema),
        defaultValues: {
            email: ""
        }
    });

    async function sendEmailLink(email: string) {
        setIsLoading(true);
        const apiClient = getApiClient();
        try {
            await apiClient.account.emailMagicLinkLoginApiV1AccountEmailMagicLinkLoginPost({
                requestBody: email
            })
            setSentToEmail(email);
            setEmailSent(true);
            toast.success("Magic link sent successfully!", {
                description: "If you have account with us, You should receive it shortly.",
                richColors: true,
                position: "top-center"

            });
        } catch (error) {
            console.error("Error sending magic link:", error);
            toast.error("Failed to send magic link. Please try again.", {
                richColors: true,
                position: "top-center"
            });

        }
        finally {
            setIsLoading(false);
        }

    }
    const onSubmit = async (data: MagicLinkFormData) => {
        await sendEmailLink(data.email);
    };

    const handleResendEmail = async () => {
        await sendEmailLink(sentToEmail);
    };

    const backToLogin = () => {
        setEmailSent(false);
        setSentToEmail("");
        form.reset();
    }

    const closeDialog = () => {
        backToLogin();
        setShowEmailDialog(false);
    };




    return (
        <div className="pt-4">
            <Button
                variant="outline"
                className="w-full"
                onClick={() => setShowEmailDialog(true)}
                disabled={isLoading}
            >
                <Mail className="w-4 h-4 text-primary" />
                Sign in with Magic Link
            </Button>


            <Dialog open={showEmailDialog} onOpenChange={closeDialog}>
                <DialogContent className="sm:max-w-lg" isFullBlack>
                    {emailSent && (
                        <>
                            <DialogHeader>
                                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                                    <CheckCircle className="h-6 w-6 text-green-600" />
                                </div>
                                <DialogTitle>Check Your Email</DialogTitle>
                                <DialogDescription>
                                    We've sent a magic link to <strong>{sentToEmail}</strong>
                                </DialogDescription>
                            </DialogHeader>
                            <section>
                                <Alert>
                                    <Mail className="h-4 w-4" />
                                    <AlertDescription>
                                        Click the link in your email to sign in instantly. The link will expire in 15 minutes.
                                    </AlertDescription>
                                </Alert>

                                <div className="text-center text-sm text-muted-foreground pt-3 pb-3 flex items-center justify-center">
                                    <span className="mr-1 block">
                                        Didn't receive the email? Check your spam folder or{" "}
                                    </span>
                                    <Button
                                        onClick={handleResendEmail}
                                        disabled={isLoading}
                                        variant="link"
                                        className="text-primary underline hover:text-primary/80 p-0"

                                    >
                                        {isLoading ? "Resending..." : "Resend it"}
                                    </Button>
                                </div>

                                <Button
                                    variant="outline"
                                    onClick={backToLogin}
                                    className="w-full"
                                    disabled={isLoading}
                                >
                                    <ArrowLeft className="w-4 h-4 mr-2" />
                                    Back to Login
                                </Button>

                                <div className="text-center text-sm text-muted-foreground border-t pt-4">
                                    Remember your password?{' '}
                                    <Button variant="link"
                                        className="text-primary underline hover:text-primary/80 p-0"
                                        onClick={closeDialog}
                                    >
                                        Sign in with password
                                    </Button>
                                </div>
                            </section>
                        </>
                    )}

                    {!emailSent && (
                        <>
                            <DialogHeader>
                                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                                    <Mail className="h-6 w-6 text-primary" />
                                </div>
                                <DialogTitle>Sign in with Magic Link</DialogTitle>
                                <DialogDescription>
                                    Enter your email address and we'll send you a secure link to sign in
                                </DialogDescription>
                            </DialogHeader>

                            <Form {...form}>
                                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
                                                            type="email"
                                                            placeholder="Enter your email address"
                                                            className="pl-10"
                                                            disabled={isLoading}
                                                            {...field}
                                                        />
                                                    </div>
                                                </FormControl>
                                                <FormDescription>
                                                    We'll send you a secure link that expires in 15 minutes
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <Button
                                        type="submit"
                                        className="w-full"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? (
                                            <>
                                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                                                Sending Magic Link...
                                            </>
                                        ) : (
                                            <>
                                                <Send className="w-4 h-4 mr-2" />
                                                Send Magic Link
                                            </>
                                        )}
                                    </Button>
                                </form>
                            </Form>

                        </>


                    )}
                </DialogContent>
            </Dialog>
        </div>
    )
}