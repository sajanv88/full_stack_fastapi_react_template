import { Dialog, DialogContent, DialogHeader, DialogTrigger, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { extractErrorMessage, getApiClient } from "@/lib/utils";
import { useAuthContext } from "../providers/auth-provider";
import { useEffect, useState } from "react";
import { RegisteredPasskeyCredentialsDto } from "@/api";
import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Plus, Trash } from "lucide-react";
import { startRegistration, WebAuthnError } from "@simplewebauthn/browser";
import { toast } from "sonner";


interface PassKeyManagementProps {
    accessToken: string;
    email?: string;
    shouldRefresh?: boolean;
}
function PassKeyManagement({ accessToken, email, shouldRefresh }: PassKeyManagementProps) {
    const [allPasskeys, setAllPasskeys] = useState<Array<RegisteredPasskeyCredentialsDto>>([]);
    const [isAdding, setIsAdding] = useState(false);
    async function fetchPasskeys() {
        const apiClient = getApiClient(accessToken);
        const passkeys = await apiClient.manageSecurity.getRegisteredPasskeysApiV1SecurityPasskeysGet();
        setAllPasskeys(passkeys);
    }

    async function onDeletePasskey(credentialId: string) {
        const apiClient = getApiClient(accessToken);
        await apiClient.manageSecurity.deleteRegisteredPasskeyApiV1SecurityPasskeysCredentialIdDelete({
            credentialId: credentialId
        });
        // Refresh the list
        fetchPasskeys();
    }

    async function onAddPasskey() {
        if (!email) return;
        setIsAdding(true);
        try {
            const account = getApiClient(accessToken).account;
            const options = await account.passkeyRegisterOptionsApiV1AccountPasskeyRegisterOptionsPost({
                requestBody: email
            });
            const credential = await startRegistration(JSON.parse(options));
            await account.passkeyRegisterApiV1AccountPasskeyRegisterPost({
                requestBody: { credential, email }
            });
            toast.success("Passkey registered successfully!", {
                description: "You can now use your passkey for future logins.",
                richColors: true
            });
            await fetchPasskeys();
        } catch (error) {
            toast.error("Could not add the passkey", {
                description: error instanceof WebAuthnError ? error.message : extractErrorMessage(error),
                richColors: true,
                position: "top-right"
            });
        } finally {
            setIsAdding(false);
        }
    }

    useEffect(() => {
        if (shouldRefresh) {
            fetchPasskeys();
        }
    }, [shouldRefresh]);

    return (
        <DialogContent>
            <DialogHeader>
                <DialogTitle>
                    List of Registered Passkeys
                </DialogTitle>
            </DialogHeader>
            <section className="mt-4 overflow-x-auto">
                <Table>
                    <TableCaption>A list of your registered passkeys.</TableCaption>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Created At</TableHead>
                            <TableHead>Last Used At</TableHead>
                            <TableHead className="text-right">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>

                        {allPasskeys.map((passkey) => (
                            <TableRow key={passkey.credential_id}>
                                <TableCell>{new Date(passkey.created_at).toLocaleString()}</TableCell>
                                <TableCell>{passkey.last_used_at ? new Date(passkey.last_used_at).toLocaleString() : "Never"}</TableCell>
                                <TableCell className="text-right">
                                    <Button variant="destructive" size="icon" onClick={() => onDeletePasskey(passkey.credential_id)}>
                                        <Trash />
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {allPasskeys.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={3} className="text-center">No registered passkeys found.</TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
                <div className="mt-4 flex justify-end">
                    <Button variant="outline" onClick={onAddPasskey} disabled={isAdding || !email}>
                        <Plus />
                        {isAdding ? "Adding..." : "Add a passkey"}
                    </Button>
                </div>
            </section>
        </DialogContent >
    )
}

export function ManageSecurity() {
    const { accessToken, user } = useAuthContext();
    const [shouldRefresh, setShouldRefresh] = useState<boolean>(false);

    function onOpen(isOpen: boolean) {
        if (isOpen && accessToken) {
            setShouldRefresh(true);
        }
        else if (!isOpen) {
            setShouldRefresh(false);
        }
    }

    return (
        <Dialog onOpenChange={onOpen}>
            <DialogTrigger asChild>
                <Button variant="outline">Manage Security</Button>
            </DialogTrigger>
            <PassKeyManagement accessToken={accessToken!} email={user?.email} shouldRefresh={shouldRefresh} />
        </Dialog>
    )
}