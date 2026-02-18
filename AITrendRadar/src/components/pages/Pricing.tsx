import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { Check, Zap, Star } from "lucide-react";
import { motion } from "motion/react";

interface PricingProps {
  onNavigate: (page: string) => void;
}

export function Pricing({ onNavigate }: PricingProps) {
  const tiers = [
    {
      name: "Starter",
      description: "For individual creators and small teams",
      price: "Free",
      features: [
        "Up to 3 seats",
        "50 alerts/month",
        "Reddit + X access",
        "Basic clustering",
        "Email support",
        "7-day trend history",
      ],
    },
    {
      name: "Professional",
      description: "For growing brands and agencies",
      price: "$14.99/mo",
      features: [
        "Up to 10 seats",
        "500 alerts/month",
        "All platform access (Reddit, X, Instagram, TikTok)",
        "Advanced clustering + influencer graph",
        "Priority support",
        "30-day trend history",
        "Custom alert rules",
        "API access",
      ],
      highlighted: true,
    },
    {
      name: "Enterprise",
      description: "For large organizations",
      price: "$49.99/mo",
      features: [
        "Unlimited seats",
        "Unlimited alerts",
        "All platforms + licensed news/blogs",
        "Full feature access",
        "Dedicated support",
        "Unlimited history",
        "Custom integrations",
        "SLA guarantee",
        "White-label options",
      ],
    },
  ];

  return (
    <div className="flex-1">
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-accent/5 via-background to-background" />
        
        <div className="relative max-w-[1200px] mx-auto px-6 lg:px-8 py-20">
          <motion.div 
            className="max-w-[800px] mx-auto text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="mb-6">Pricing</h1>
            <p className="text-xl text-muted-foreground">
              Choose the plan that fits your trend intelligence needs
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {tiers.map((tier, index) => (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: tier.highlighted ? 0 : -8 }}
              >
                <Card
                  className={`p-8 h-full relative overflow-hidden transition-all duration-300 ${
                    tier.highlighted 
                      ? "border-accent border-2 shadow-2xl scale-105 bg-gradient-to-br from-accent/5 to-transparent" 
                      : "hover:border-accent/30 hover:shadow-xl"
                  }`}
                >
                  {tier.highlighted && (
                    <>
                      <div className="absolute top-0 right-0 left-0 h-1 bg-gradient-to-r from-accent via-accent-secondary to-accent" />
                      <div className="flex items-center gap-2 text-xs font-medium text-accent mb-4">
                        <Star className="w-4 h-4 fill-accent" />
                        MOST POPULAR
                      </div>
                    </>
                  )}
                  <h3 className="mb-2">{tier.name}</h3>
                  <p className="text-sm text-muted-foreground mb-6">{tier.description}</p>
                  <div className="mb-6">
                    <div className={`text-4xl font-semibold ${tier.highlighted ? "bg-gradient-to-r from-accent to-accent-secondary bg-clip-text text-transparent" : ""}`}>
                      {tier.price}
                    </div>
                  </div>
                  <Button
                    className={`w-full mb-6 group relative overflow-hidden ${
                      tier.highlighted 
                        ? "bg-gradient-to-r from-accent to-accent-secondary hover:shadow-lg" 
                        : ""
                    }`}
                    variant={tier.highlighted ? "default" : "outline"}
                    onClick={() => onNavigate("contact")}
                  >
                    <span className="relative z-10 flex items-center gap-2">
                      Get Started
                      {tier.highlighted && <Zap className="w-4 h-4" />}
                    </span>
                  </Button>
                  <div className="space-y-3">
                    {tier.features.map((feature, i) => (
                      <motion.div 
                        key={feature} 
                        className="flex gap-3 items-start group"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 + i * 0.05 }}
                      >
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                          tier.highlighted 
                            ? "bg-gradient-to-br from-accent to-accent-secondary" 
                            : "bg-accent/10"
                        }`}>
                          <Check className={`w-3 h-3 ${tier.highlighted ? "text-white" : "text-accent"}`} />
                        </div>
                        <span className="text-sm">{feature}</span>
                      </motion.div>
                    ))}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>

          <motion.div 
            className="bg-gradient-to-br from-muted/50 to-muted/30 rounded-2xl p-8 max-w-[800px] mx-auto border border-border/50 shadow-lg"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h3 className="mb-4">Usage-Based Options Available</h3>
            <p className="text-muted-foreground mb-4">
              We offer flexible usage-based pricing for:
            </p>
            <ul className="space-y-2 text-muted-foreground mb-6">
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent" />
                Per-alert pricing for high-volume scenarios
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent" />
                Platform-specific access (e.g., Instagram PCAA gating)
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent" />
                Custom data retention periods
              </li>
              <li className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent" />
                API rate limit tiers
              </li>
            </ul>
            <Button 
              variant="outline" 
              className="hover:bg-accent hover:text-white hover:border-accent transition-all duration-300" 
              onClick={() => onNavigate("contact")}
            >
              Contact Sales for Custom Pricing
            </Button>
          </motion.div>

          <motion.div 
            className="mt-16 text-center max-w-[700px] mx-auto"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h3 className="mb-8">Key Performance Indicators</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { value: "2-5d", label: "Lead Time" },
                { value: "85%+", label: "Precision" },
                { value: "80%+", label: "Recall" },
                { value: "99.5%", label: "Uptime" },
              ].map((kpi, i) => (
                <motion.div
                  key={kpi.label}
                  className="p-6 bg-gradient-to-br from-accent/10 to-transparent rounded-xl border border-accent/20 hover:border-accent/40 transition-all duration-300 hover:shadow-lg cursor-pointer"
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  whileHover={{ scale: 1.05, y: -4 }}
                >
                  <div className="text-3xl font-semibold bg-gradient-to-br from-accent to-accent-secondary bg-clip-text text-transparent">
                    {kpi.value}
                  </div>
                  <div className="text-sm text-muted-foreground mt-2">{kpi.label}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}