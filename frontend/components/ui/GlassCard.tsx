"use client";
import { forwardRef } from "react";
import { clsx } from "clsx";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    hover?: boolean;
    glow?: "purple" | "amber" | "none";
    padding?: "sm" | "md" | "lg";
}

const paddings = { sm: "p-4", md: "p-6", lg: "p-8" };
const glows = {
    purple: "hover:border-zia-purple/40 hover:shadow-[0_0_20px_rgba(108,77,230,0.2)]",
    amber: "hover:border-zia-amber/40 hover:shadow-glow-amber",
    none: "",
};

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
    ({ children, className, hover = false, glow = "none", padding = "md", ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={clsx(
                    "glass-card",
                    paddings[padding],
                    hover && [
                        "transition-all duration-300 cursor-pointer",
                        "hover:bg-white/[0.08] hover:-translate-y-0.5",
                        glows[glow],
                    ],
                    className
                )}
                {...props}
            >
                {children}
            </div>
        );
    }
);
GlassCard.displayName = "GlassCard";
