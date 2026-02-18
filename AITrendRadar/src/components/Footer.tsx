interface FooterProps {
  onNavigate: (page: string) => void;
}

export function Footer({ onNavigate }: FooterProps) {
  return (
    <footer className="border-t border-border bg-gradient-to-b from-muted/30 to-muted/50">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4 group cursor-pointer" onClick={() => onNavigate("home")}>
              <div className="w-8 h-8 bg-gradient-to-br from-accent to-accent-secondary rounded-lg flex items-center justify-center shadow-md group-hover:shadow-lg group-hover:scale-110 transition-all">
                <span className="text-accent-foreground font-semibold">TR</span>
              </div>
              <span className="font-semibold group-hover:text-accent transition-colors">Trend Radar</span>
            </div>
            <p className="text-muted-foreground text-sm">
              Real-time social trend detection, lifecycle prediction, and marketer recommendations.
            </p>
          </div>

          <div>
            <h4 className="font-medium mb-4">Legal</h4>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => onNavigate("privacy")}
                className="text-sm text-muted-foreground hover:text-accent transition-all text-left hover:translate-x-1 duration-300"
              >
                → Privacy Policy
              </button>
              <button
                onClick={() => onNavigate("terms")}
                className="text-sm text-muted-foreground hover:text-accent transition-all text-left hover:translate-x-1 duration-300"
              >
                → Terms of Service
              </button>
            </div>
          </div>

          <div>
            <h4 className="font-medium mb-4">Contact</h4>
            <a 
              href="mailto:help@trendradar.com"
              className="text-sm text-muted-foreground hover:text-accent transition-colors block"
            >
              Email: help@trendradar.com
            </a>
            <p className="text-sm text-muted-foreground mt-2">
              All data sourced through ToS-compliant public APIs
            </p>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-border/50">
          <p className="text-sm text-muted-foreground text-center">
            © 2025 Trend Radar. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}