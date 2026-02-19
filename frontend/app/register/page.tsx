"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { register as apiRegister } from "@/lib/api/auth";
import { useAuth } from "@/contexts/AuthContext";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";

export default function RegisterPage() {
    const { login } = useAuth();
    const router = useRouter();
    const [displayName, setDisplayName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const inputClass =
        "w-full bg-white/[0.06] border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 text-sm focus:outline-none focus:border-zia-purple/60 focus:bg-white/[0.08] transition-all duration-200";

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (password.length < 8) { setError("Password must be at least 8 characters."); return; }
        setError(null);
        setLoading(true);
        try {
            await apiRegister(email, password, displayName || undefined);
            await login(email, password);
            router.push("/");
        } catch {
            setError("Registration failed. Email may already be in use.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center px-4 py-12">
            <GlassCard className="w-full max-w-sm space-y-5">
                <div className="text-center space-y-1">
                    <div className="w-12 h-12 rounded-full bg-zia-mic mx-auto mb-3 flex items-center justify-center text-xl font-bold shadow-mic-idle">Z</div>
                    <h1 className="text-white text-xl font-bold">Create your account</h1>
                    <p className="text-white/40 text-sm">Join Zia AI</p>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-1.5">
                        <label className="text-white/50 text-xs uppercase tracking-wider">Display Name</label>
                        <input type="text" placeholder="Alex" className={inputClass} value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
                    </div>
                    <div className="space-y-1.5">
                        <label className="text-white/50 text-xs uppercase tracking-wider">Email</label>
                        <input type="email" required placeholder="you@example.com" className={inputClass} value={email} onChange={(e) => setEmail(e.target.value)} />
                    </div>
                    <div className="space-y-1.5">
                        <label className="text-white/50 text-xs uppercase tracking-wider">Password</label>
                        <input type="password" required minLength={8} placeholder="Min. 8 characters" className={inputClass} value={password} onChange={(e) => setPassword(e.target.value)} />
                    </div>
                    {error && <p className="text-red-400 text-sm bg-red-500/10 rounded-xl px-3 py-2">{error}</p>}
                    <Button type="submit" isLoading={loading} className="w-full" size="lg">Create Account</Button>
                </form>
                <p className="text-center text-white/40 text-sm">
                    Already have an account?{" "}
                    <a href="/login" className="text-zia-violet hover:text-white transition-colors">Sign in</a>
                </p>
            </GlassCard>
        </main>
    );
}
