"use client";

import { ButtonHTMLAttributes, cloneElement, forwardRef, isValidElement, ReactElement, ReactNode } from "react";

import { cn } from "@/utils/cn";

type ButtonVariant = "default" | "secondary" | "ghost" | "outline";
type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  asChild?: boolean;
  children?: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  default:
    "bg-primary text-primary-foreground shadow-soft hover:translate-y-[-1px] hover:shadow-xl",
  secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90",
  ghost: "bg-transparent text-foreground hover:bg-muted",
  outline: "border border-border bg-card text-foreground hover:bg-muted",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-5 text-sm",
  lg: "h-12 px-6 text-base",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { className, variant = "default", size = "md", type = "button", asChild = false, children, ...props },
  ref,
) {
  const combinedClassName = cn(
    "inline-flex items-center justify-center rounded-2xl font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/40 disabled:pointer-events-none disabled:opacity-50",
    variantClasses[variant],
    sizeClasses[size],
    className,
  );

  if (asChild && isValidElement(children)) {
    return cloneElement(children as ReactElement<Record<string, unknown>>, {
      className: cn((children.props as { className?: string }).className, combinedClassName),
      ...props,
    });
  }

  return (
    <button
      ref={ref}
      type={type}
      className={combinedClassName}
      {...props}
    >
      {children}
    </button>
  );
});
