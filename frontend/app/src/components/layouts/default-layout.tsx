import { DarkMode } from "@/components/features/dark-mode/dark-mode"
import { Outlet } from "react-router";
import { Toaster } from 'sonner'
export function DefaultLayout() {

    return (
        <div className="grid grid-rows-[auto_1fr_auto] h-screen gap-4 text-accent-foreground bg-primary-foreground">
            <header className="p-4 bg-secondary">
                <section className="flex justify-between items-center">
                    <h1 className="text-xl font-bold text-primary">
                    </h1>
                    <DarkMode />
                </section>
            </header>
            <main>
                <Outlet />
                <Toaster />
            </main>
            <footer className="p-4 bg-accent">
                <p>Footer content</p>
            </footer>
        </div>
    );
}
