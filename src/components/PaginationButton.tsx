import { Button } from "@/components/ui/button";

export function PaginationButton({ children, isActive, onClick }: { children: React.ReactNode; isActive?: boolean; onClick?: () => void }) {
  return (
    <Button
      variant={isActive ? "default" : "outline"}
      size="sm"
      onClick={onClick}
      className={isActive ? "bg-primary text-primary-foreground" : ""}
    >
      {children}
    </Button>
  );
} 