import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const alertBannerVariants = cva(
  "relative w-full rounded-md border p-4 flex items-start gap-3",
  {
    variants: {
      variant: {
        default: "bg-background text-foreground",
        info: "border-status-info/30 bg-status-info/10 text-foreground [&>svg]:text-status-info",
        success:
          "border-status-success/30 bg-status-success/10 text-foreground [&>svg]:text-status-success",
        warning:
          "border-status-warning/30 bg-status-warning/10 text-foreground [&>svg]:text-status-warning",
        destructive:
          "border-destructive/30 bg-destructive/10 text-foreground [&>svg]:text-destructive",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

interface AlertBannerProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertBannerVariants> {}

const AlertBanner = forwardRef<HTMLDivElement, AlertBannerProps>(
  ({ className, variant, ...props }, ref) => (
    <div
      ref={ref}
      role="alert"
      className={cn(alertBannerVariants({ variant }), className)}
      {...props}
    />
  ),
);
AlertBanner.displayName = "AlertBanner";

const AlertBannerTitle = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("font-medium leading-none tracking-tight", className)}
    {...props}
  />
));
AlertBannerTitle.displayName = "AlertBannerTitle";

const AlertBannerDescription = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm [&_p]:leading-relaxed", className)}
    {...props}
  />
));
AlertBannerDescription.displayName = "AlertBannerDescription";

export {
  AlertBanner,
  AlertBannerDescription,
  AlertBannerTitle,
  alertBannerVariants,
};
