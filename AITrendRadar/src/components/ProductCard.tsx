import { Card } from "./ui/card";
import { LucideIcon } from "lucide-react";

interface ProductCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  visual?: React.ReactNode;
}

export function ProductCard({ title, description, icon: Icon, visual }: ProductCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-xl transition-all duration-300 border-2 hover:border-accent/30 hover:-translate-y-1 group cursor-pointer">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-md group-hover:shadow-lg group-hover:scale-110 transition-all duration-300">
            <Icon className="w-6 h-6 text-white" />
          </div>
          <h3 className="group-hover:text-accent transition-colors">{title}</h3>
        </div>
        <p className="text-muted-foreground">{description}</p>
      </div>
      {visual && (
        <div className="bg-gradient-to-br from-accent/5 to-transparent p-6 border-t border-accent/20">
          {visual}
        </div>
      )}
    </Card>
  );
}