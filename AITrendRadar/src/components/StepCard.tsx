import { Card } from "./ui/card";
import { LucideIcon } from "lucide-react";

interface StepCardProps {
  number: string;
  title: string;
  description: string;
  icon: LucideIcon;
}

export function StepCard({ number, title, description, icon: Icon }: StepCardProps) {
  return (
    <Card className="p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
            <Icon className="w-6 h-6 text-accent" />
          </div>
        </div>
        <div className="flex-1">
          <div className="text-sm text-muted-foreground mb-1">Step {number}</div>
          <h3 className="mb-2">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
    </Card>
  );
}