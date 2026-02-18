import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { TrendBadge } from "../TrendBadge";
import { Check, TrendingUp, Zap, Shield, ArrowRight, Sparkles } from "lucide-react";
import { motion } from "motion/react";

interface HomeProps {
  onNavigate: (page: string) => void;
}

export function Home({ onNavigate }: HomeProps) {
  return (
    <div className="flex-1">
      {/* Hero Section with Gradient Background */}
      <section className="relative overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-background to-accent/10" 
             style={{ 
               backgroundSize: '200% 200%',
               animation: 'gradient 15s ease infinite'
             }} />
        
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 opacity-[0.05]" 
             style={{
               backgroundImage: `linear-gradient(to right, rgba(255,255,255,0.1) 1px, transparent 1px),
                                linear-gradient(to bottom, rgba(255,255,255,0.1) 1px, transparent 1px)`,
               backgroundSize: '40px 40px'
             }} />

        <div className="relative max-w-[1200px] mx-auto px-6 lg:px-8 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <motion.div 
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 border border-accent/20 mb-6"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Sparkles className="w-4 h-4 text-accent" />
                <span className="text-sm font-medium text-accent">AI-Powered Trend Intelligence</span>
              </motion.div>
              
              <h1 style={{ fontSize: 'var(--text-display)', lineHeight: 'var(--text-display-lh)' }} className="mb-6">
                Trend Radar
              </h1>
              <p className="text-xl text-muted-foreground mb-8 max-w-[600px]">
                Unify public signals to detect spikes, cluster topics, forecast lifecycle, and get marketer recommendations—earlier.
              </p>
              <div className="flex flex-wrap gap-4">
                <Button 
                  size="lg" 
                  onClick={() => onNavigate("contact")}
                  className="group relative overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    Request Pilot
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </span>
                  <div className="absolute inset-0 bg-accent-secondary translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                </Button>
                <Button 
                  size="lg" 
                  variant="outline" 
                  onClick={() => onNavigate("how-it-works")}
                  className="hover:bg-accent/5 hover:border-accent transition-all duration-300"
                >
                  See How It Works
                </Button>
              </div>
            </motion.div>

            <motion.div 
              className="relative"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              {/* Floating glow effect */}
              <div className="absolute -inset-4 bg-gradient-to-r from-accent/20 to-accent/5 rounded-3xl blur-2xl"
                   style={{ animation: 'pulse-glow 3s ease-in-out infinite' }} />
              
              <Card className="relative p-6 border-2 hover:border-accent/30 transition-all duration-500 shadow-xl hover:shadow-2xl">
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">Trending Topics</div>
                    <div className="flex flex-wrap gap-2">
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <TrendBadge stage="emerging" />
                      </motion.div>
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <TrendBadge stage="rising" />
                      </motion.div>
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <TrendBadge stage="peaking" />
                      </motion.div>
                    </div>
                  </div>
                  <div className="h-32 bg-gradient-to-br from-accent/5 to-accent/10 rounded-lg flex items-center justify-center border border-accent/20">
                    <motion.div 
                      className="text-center text-muted-foreground"
                      animate={{ y: [0, -10, 0] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <TrendingUp className="w-8 h-8 mx-auto mb-2 text-accent" />
                      <div className="text-sm">Lifecycle Timeline</div>
                    </motion.div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <motion.div 
                      className="p-3 bg-gradient-to-br from-accent/5 to-transparent rounded-lg border border-accent/10 hover:border-accent/30 transition-all cursor-pointer"
                      whileHover={{ scale: 1.05, y: -2 }}
                    >
                      <div className="font-semibold text-accent">247</div>
                      <div className="text-xs text-muted-foreground">Signals</div>
                    </motion.div>
                    <motion.div 
                      className="p-3 bg-gradient-to-br from-accent/5 to-transparent rounded-lg border border-accent/10 hover:border-accent/30 transition-all cursor-pointer"
                      whileHover={{ scale: 1.05, y: -2 }}
                    >
                      <div className="font-semibold text-accent">89%</div>
                      <div className="text-xs text-muted-foreground">Accuracy</div>
                    </motion.div>
                    <motion.div 
                      className="p-3 bg-gradient-to-br from-accent/5 to-transparent rounded-lg border border-accent/10 hover:border-accent/30 transition-all cursor-pointer"
                      whileHover={{ scale: 1.05, y: -2 }}
                    >
                      <div className="font-semibold text-accent">3.2d</div>
                      <div className="text-xs text-muted-foreground">Lead Time</div>
                    </motion.div>
                  </div>
                </div>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Trust Bullets */}
      <section className="bg-gradient-to-r from-muted/50 via-muted/30 to-muted/50 border-y border-border">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8 py-16">
          <div className="grid md:grid-cols-3 gap-8">
            <motion.div 
              className="flex gap-4 group"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0 }}
            >
              <div className="flex-shrink-0">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300">
                  <Shield className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h4 className="mb-2 group-hover:text-accent transition-colors">ToS-Compliant Sources</h4>
                <p className="text-sm text-muted-foreground">
                  Only official APIs: Reddit, X, Instagram Graph, TikTok developer surfaces, licensed blogs/news
                </p>
              </div>
            </motion.div>

            <motion.div 
              className="flex gap-4 group"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex-shrink-0">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300">
                  <Zap className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h4 className="mb-2 group-hover:text-accent transition-colors">Early Lead Time</h4>
                <p className="text-sm text-muted-foreground">
                  Detect emerging trends 2–5 days before they peak, giving you time to act
                </p>
              </div>
            </motion.div>

            <motion.div 
              className="flex gap-4 group"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex-shrink-0">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300">
                  <Check className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h4 className="mb-2 group-hover:text-accent transition-colors">Measurable KPIs</h4>
                <p className="text-sm text-muted-foreground">
                  Track precision, recall, lead time, and adoption metrics to prove ROI
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* How It Works Preview */}
      <section className="max-w-[1200px] mx-auto px-6 lg:px-8 py-20">
        <motion.div 
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="mb-4">How It Works</h2>
          <p className="text-muted-foreground max-w-[600px] mx-auto">
            From raw signals to actionable recommendations in six automated steps
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {[
            { num: 1, title: "Ingest", desc: "Official APIs feed real-time data", delay: 0 },
            { num: 2, title: "Detect", desc: "STL + z-score identify spikes", delay: 0.1 },
            { num: 3, title: "Cluster", desc: "e5 + HDBSCAN group topics", delay: 0.2 },
            { num: 4, title: "Forecast", desc: "FSM tracks lifecycle stages", delay: 0.3 },
            { num: 5, title: "Recommend", desc: "Channels, timing, and content", delay: 0.4 },
            { num: 6, title: "Alert", desc: "Rules notify your team", delay: 0.5 },
          ].map((step) => (
            <motion.div
              key={step.num}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: step.delay }}
              whileHover={{ y: -8, scale: 1.02 }}
            >
              <Card className="p-6 h-full border-2 hover:border-accent/40 hover:shadow-xl transition-all duration-300 cursor-pointer relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="relative">
                  <div className="text-3xl font-semibold mb-2 bg-gradient-to-br from-accent to-accent-secondary bg-clip-text text-transparent">
                    {step.num}. {step.title}
                  </div>
                  <p className="text-sm text-muted-foreground">{step.desc}</p>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div 
          className="text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.6 }}
        >
          <Button 
            onClick={() => onNavigate("how-it-works")} 
            variant="outline"
            className="group hover:bg-accent hover:text-white hover:border-accent transition-all duration-300"
          >
            Learn More About Our Process
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </Button>
        </motion.div>
      </section>
    </div>
  );
}