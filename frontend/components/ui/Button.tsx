"use client";
import { forwardRef } from "react";
import { clsx } from "clsx";

type ButtonVariant = "primary" | "ghost" | "danger" | "outline";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
    isLoading?: boolean;
    leftIcon?: React.ReactNode;
}

const variants: Record<ButtonVariant, string> = {
    primary:
        "bg-zia-purple hover:bg-zia-glow text-white shadow-[0_0_20px_rgba(108,77,230,0.4)] hover:shadow-[0_0_30px_rgba(139,92,246,0.6)]",
    ghost:
        "bg-white/5 hover:bg-white/10 text-white/80 hover:text-white border border-white/10 hover:border-white/20",
    danger:
        "bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 hover:border-red-500/50",
    outline:
        "bg-transparent border border-zia-purple/50 text-zia-violet hover:bg-zia-purple/10 hover:border-zia-purple",
};

const sizes: Record<ButtonSize, string> = {
    sm: "px-3 py-1.5 text-sm rounded-lg",
    md: "px-5 py-2.5 text-sm rounded-xl",
    lg: "px-7 py-3.5 text-base rounded-2xl",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            children,
            className,
            variant = "primary",
            size = "md",
            isLoading,
            leftIcon,
            disabled,
            ...props
        },
        ref
    ) => (
        <button
            ref={ref}
            disabled={disabled || isLoading}
            className={clsx(
                "inline-flex items-center justify-center gap-2 font-medium font-sora transition-all duration-200",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zia-purple/60",
                "disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none",
                variants[variant],
                sizes[size],
                className
            )}
            {...props}
        >
            {isLoading ? (
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
            ) : (
                leftIcon
            )}
            {children}
        </button>
    )
);
Button.displayName = "Button";
