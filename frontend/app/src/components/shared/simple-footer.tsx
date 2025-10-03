import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
    Heart,
} from 'lucide-react'
import { Logo } from './logo'

export function SimpleFooter() {
    const currentYear = new Date().getFullYear()
    return (
        <footer className="bg-background border-t border-border mx-5">
            <div className=" px-4 py-6">
                <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
                    {/* Brand */}
                    <div className="flex items-center space-x-2">
                        <Logo size='sm' />
                        <Badge variant="outline" className="text-xs">v1.0.0</Badge>
                    </div>


                </div>

                <Separator className="my-4" />

                <div className="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
                    <p className="text-sm text-muted-foreground">
                        © {currentYear} FullStack Template. All rights reserved.
                    </p>

                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <span>Made with</span>
                        <Heart className="w-3 h-3 text-red-500 fill-current" />
                        <span>for developers</span>
                    </div>
                </div>
            </div>
        </footer>
    )
}
