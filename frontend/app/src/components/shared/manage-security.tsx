import { Dialog, DialogContent, DialogHeader, DialogTrigger, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { getApiClient } from "@/lib/utils";
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
import { Trash } from "lucide-react";


interface PassKeyManagementProps {
    accessToken: string;
    shouldRefresh?: boolean;
}
function PassKeyManagement({ accessToken, shouldRefresh }: PassKeyManagementProps) {
    const [allPasskeys, setAllPasskeys] = useState<Array<RegisteredPasskeyCredentialsDto>>([]);
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

    useEffect(() => {
        if (shouldRefresh) {
            fetchPasskeys();
        }
    }, [shouldRefresh]);

    return (
        <DialogContent className="sm:max-w-screen-md">
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
            </section>
        </DialogContent >
    )
}

export function ManageSecurity() {
    const { accessToken } = useAuthContext();
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
            <PassKeyManagement accessToken={accessToken!} shouldRefresh={shouldRefresh} />
        </Dialog>
    )
}