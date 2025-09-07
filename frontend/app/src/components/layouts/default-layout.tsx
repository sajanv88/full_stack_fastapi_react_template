import { DarkMode } from "@/components/features/dark-mode/dark-mode"
import { Footer } from "@/components/shared/footer"
import { Outlet } from "react-router";
import { Toaster } from 'sonner'
export function DefaultLayout() {

    return (
        <div className="flex flex-col min-h-screen bg-primary-foreground">
            <header className="p-4 bg-secondary border-b border-border">
                <section className="container mx-auto flex justify-between items-center">
                    <h1 className="text-xl font-bold text-primary">
                        FullStack Template
                    </h1>
                    <DarkMode />
                </section>
            </header>
            <main className="flex-1">
                <Outlet />
                <Toaster />
            </main>
            <Footer />
        </div>
    );
}
