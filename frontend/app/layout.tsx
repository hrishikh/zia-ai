import type { Metadata } from "next";
import { AuthProvider } from "@/contexts/AuthContext";
import { WebSocketProvider } from "@/contexts/WebSocketContext";
import { ConfirmProvider } from "@/contexts/ConfirmContext";
import "@/styles/globals.css";

export const metadata: Metadata = {
    title: "Zia AI",
    description: "Your production-grade AI assistant",
    themeColor: "#0b0d1a",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en" className="dark">
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
            </head>
            <body className="font-sora antialiased">
                <AuthProvider>
                    <ConfirmProvider>
                        <WebSocketProvider>
                            {children}
                        </WebSocketProvider>
                    </ConfirmProvider>
                </AuthProvider>
            </body>
        </html>
    );
}
