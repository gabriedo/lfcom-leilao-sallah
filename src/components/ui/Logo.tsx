import { cn } from "@/lib/utils"

interface LogoProps {
  className?: string
  variant?: "default" | "small" | "large"
  theme?: "light" | "dark"
}

export function Logo({ 
  className, 
  variant = "default",
  theme = "light" 
}: LogoProps) {
  const sizes = {
    small: "h-6 w-6",
    default: "h-8 w-8",
    large: "h-12 w-12"
  }

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <img 
        src={theme === "light" ? "/assets/images/logo.svg" : "/assets/images/logo-dark.svg"}
        alt="LFCOM Logo"
        className={cn(sizes[variant])}
      />
      <span className={cn(
        "font-bold tracking-tight",
        variant === "small" && "text-lg",
        variant === "default" && "text-xl",
        variant === "large" && "text-2xl",
        theme === "dark" ? "text-white" : "text-lfcom-black"
      )}>
        LFCOM
      </span>
    </div>
  )
} 