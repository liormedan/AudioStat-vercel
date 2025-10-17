import * as React from "react";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "secondary" | "destructive";
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "default", ...props }, ref) => {
    const base = "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus:ring-2 focus:ring-offset-2";
    const variants: Record<string, string> = {
      default: "bg-cyan-500 text-black hover:bg-cyan-400 focus:ring-cyan-500 ring-offset-[var(--panel)]",
      secondary: "bg-slate-700 text-white hover:bg-slate-600 focus:ring-slate-400 ring-offset-[var(--panel)]",
      destructive: "bg-red-500 text-white hover:bg-red-400 focus:ring-red-500 ring-offset-[var(--panel)]",
    };
    const cls = `${base} ${variants[variant]} ${className}`.trim();
    return <button ref={ref} className={cls} {...props} />;
  }
);
Button.displayName = "Button";

