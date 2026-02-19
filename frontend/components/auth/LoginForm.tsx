"use client";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";

export function LoginForm() {
    const { login } = useAuth();
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            console.log("[LoginForm] submitting", { email });
            await login(email, password);
            router.push("/");
        } catch (err: unknown) {
            // Show the actual backend error detail if available
            const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string };
            const detail = axiosErr?.response?.data?.detail ?? axiosErr?.message ?? "Login failed";
            console.error("[LoginForm] login error:", detail, err);
            setError(detail);
        } finally {
            setLoading(false);
        }
    };

    return (
        <GlassCard className="w-full max-w-sm space-y-5">
            <div className="text-center space-y-1">
                <div className="w-12 h-12 rounded-full bg-zia-mic mx-auto mb-3 flex items-center justify-center text-xl font-bold shadow-mic-idle">Z</div>
                <h1 className="text-white text-xl font-bold">Welcome back</h1>
                <p className="text-white/40 text-sm">Sign in to Zia AI</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                    <label className="text-white/50 text-xs uppercase tracking-wider">Email</label>
                    <input
                        type="email" required autoComplete="email"
                        value={email} onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        className="w-full bg-white/[0.06] border border-white/10 rounded-xl px-4 py-3
                       text-white placeholder:text-white/30 text-sm
                       focus:outline-none focus:border-zia-purple/60 focus:bg-white/[0.08]
                       transition-all duration-200"
                    />
                </div>

                <div className="space-y-1.5">
                    <label className="text-white/50 text-xs uppercase tracking-wider">Password</label>
                    <input
                        type="password" required autoComplete="current-password"
                        value={password} onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full bg-white/[0.06] border border-white/10 rounded-xl px-4 py-3
                       text-white placeholder:text-white/30 text-sm
                       focus:outline-none focus:border-zia-purple/60 focus:bg-white/[0.08]
                       transition-all duration-200"
                    />
                </div>

                {error && (
                    <p className="text-red-400 text-sm bg-red-500/10 rounded-xl px-3 py-2">{error}</p>
                )}

                <Button type="submit" isLoading={loading} className="w-full" size="lg">
                    Sign In
                </Button>
            </form>

            <p className="text-center text-white/40 text-sm">
                No account?{" "}
                <a href="/register" className="text-zia-violet hover:text-white transition-colors">
                    Register
                </a>
            </p>
        </GlassCard>
    );
}
