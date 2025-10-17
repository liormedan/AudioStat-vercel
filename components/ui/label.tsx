import * as React from "react";

export type LabelProps = React.LabelHTMLAttributes<HTMLLabelElement>;

export const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className = "", ...props }, ref) => {
    const base = "grid gap-1 text-sm";
    const cls = `${base} ${className}`.trim();
    return <label ref={ref} className={cls} {...props} />;
  }
);
Label.displayName = "Label";

