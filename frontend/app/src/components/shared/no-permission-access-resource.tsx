import { IconAlertCircle } from "@tabler/icons-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface NoPermissionProps {
    message?: string;
}
export function NoPermissionToAccessResource({ message }: NoPermissionProps) {
    return (
        <Alert>
            <IconAlertCircle className="h-4 w-4" />
            <AlertTitle>Attention!</AlertTitle>
            <AlertDescription>
                You do not have the necessary permissions to access the {message || 'resource'}. Please contact your administrator.
            </AlertDescription>
        </Alert>
    )
}
