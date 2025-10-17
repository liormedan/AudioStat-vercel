import * as React from "react";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className = "", ...props }, ref) => {
    const base = "rounded-md bg-[var(--panel)] px-3 py-2 outline-none ring-1 ring-slate-700 focus:ring-cyan-500";
    const cls = `${base} ${className}`.trim();
    return <input ref={ref} className={cls} {...props} />;
  }
);
Input.displayName = "Input";

