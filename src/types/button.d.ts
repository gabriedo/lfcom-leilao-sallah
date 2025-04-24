declare module "@/components/ui/button" {
  import { ButtonHTMLAttributes, ForwardRefExoticComponent, RefAttributes } from "react";
  import { VariantProps } from "class-variance-authority";

  export interface ButtonProps
    extends ButtonHTMLAttributes<HTMLButtonElement>,
      VariantProps<typeof buttonVariants> {
    asChild?: boolean;
  }

  export const Button: ForwardRefExoticComponent<
    ButtonProps & RefAttributes<HTMLButtonElement>
  >;

  export const buttonVariants: any;
} 