import { ProductCard } from "../ProductCard";
import { TrendBadge } from "../TrendBadge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { TrendingUp, Grid3x3, Network, Bell } from "lucide-react";
import { motion } from "motion/react";

export function Product() {
  return (
    <div className="flex-1">
      <section className="relative overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 bg-gradient-to-b from-accent/5 to-background" />
        
        <div className="relative max-w-[1200px] mx-auto px-6 lg:px-8 py-20">
          <motion.div 
            className="max-w-[800px] mx-auto text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="mb-6">Product & Results</h1>
            <p className="text-xl text-muted-foreground">
              Comprehensive trend intelligence across detection, clustering, prediction, and recommendations
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Tabs defaultValue="timeline" className="mb-16">
              <TabsList className="grid w-full max-w-[600px] mx-auto grid-cols-4 bg-muted/50 p-1 h-auto">
                <TabsTrigger value="timeline" className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-accent data-[state=active]:to-accent-secondary data-[state=active]:text-white transition-all duration-300">
                  Timeline
                </TabsTrigger>
                <TabsTrigger value="clusters" className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-accent data-[state=active]:to-accent-secondary data-[state=active]:text-white transition-all duration-300">
                  Clusters
                </TabsTrigger>
                <TabsTrigger value="influencers" className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-accent data-[state=active]:to-accent-secondary data-[state=active]:text-white transition-all duration-300">
                  Influencers
                </TabsTrigger>
                <TabsTrigger value="alerts" className="data-[state=active]:bg-gradient-to-br data-[state=active]:from-accent data-[state=active]:to-accent-secondary data-[state=active]:text-white transition-all duration-300">
                  Alerts
                </TabsTrigger>
              </TabsList>

              <TabsContent value="timeline" className="mt-8">
                <motion.div 
                  className="bg-card border-2 border-border rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <h3 className="mb-6">Trend Lifecycle Timeline</h3>
                  <div className="space-y-4">
                    {[
                      { day: "Day 1-2", stage: "emerging" as const, color: "bg-gradient-to-r from-blue-400 to-blue-600" },
                      { day: "Day 3-5", stage: "rising" as const, color: "bg-gradient-to-r from-green-400 to-green-600" },
                      { day: "Day 6-8", stage: "peaking" as const, color: "bg-gradient-to-r from-orange-400 to-orange-600" },
                      { day: "Day 9-12", stage: "declining" as const, color: "bg-gradient-to-r from-yellow-400 to-yellow-600" },
                      { day: "Day 13+", stage: "dead" as const, color: "bg-gradient-to-r from-gray-400 to-gray-600" },
                    ].map((item, index) => (
                      <motion.div
                        key={item.stage}
                        className="flex items-center gap-4 group"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <div className="w-24 text-sm text-muted-foreground font-medium">{item.day}</div>
                        <TrendBadge stage={item.stage} />
                        <div className="flex-1 h-3 bg-muted/30 rounded-full overflow-hidden relative">
                          <motion.div 
                            className={`h-full ${item.color} rounded-full`}
                            initial={{ width: 0 }}
                            animate={{ width: "100%" }}
                            transition={{ delay: index * 0.1 + 0.3, duration: 0.8, ease: "easeOut" }}
                          />
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-6 p-4 bg-accent/5 rounded-lg border border-accent/20">
                    Visual representation of trend progression through lifecycle stages with engagement metrics
                  </p>
                </motion.div>
              </TabsContent>

              <TabsContent value="clusters" className="mt-8">
                <motion.div 
                  className="bg-card border-2 border-border rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <h3 className="mb-6">Topic Clusters</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {["AI Tools", "Sustainability", "Gaming", "Fashion Tech", "Food Trends", "Fitness", "Travel", "Finance"].map((topic, i) => (
                      <motion.div 
                        key={topic} 
                        className="p-4 bg-gradient-to-br from-accent/10 to-transparent rounded-xl text-center border border-accent/20 hover:border-accent/40 hover:shadow-lg transition-all duration-300 cursor-pointer group"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.05 }}
                        whileHover={{ scale: 1.05, y: -4 }}
                      >
                        <div className="font-medium group-hover:text-accent transition-colors">{topic}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {Math.floor(Math.random() * 50 + 10)} signals
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-6 p-4 bg-accent/5 rounded-lg border border-accent/20">
                    Automated topic clustering groups related signals using e5 embeddings and HDBSCAN
                  </p>
                </motion.div>
              </TabsContent>

              <TabsContent value="influencers" className="mt-8">
                <motion.div 
                  className="bg-card border-2 border-border rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <h3 className="mb-6">Influencer Graph</h3>
                  <div className="h-64 bg-gradient-to-br from-accent/5 to-accent/10 rounded-xl flex items-center justify-center border border-accent/20 relative overflow-hidden">
                    {/* Animated background nodes */}
                    <div className="absolute inset-0 opacity-20">
                      <div className="absolute top-1/4 left-1/4 w-4 h-4 bg-accent rounded-full animate-pulse" />
                      <div className="absolute top-1/2 right-1/3 w-3 h-3 bg-accent rounded-full animate-pulse" style={{ animationDelay: "0.5s" }} />
                      <div className="absolute bottom-1/4 left-1/2 w-5 h-5 bg-accent rounded-full animate-pulse" style={{ animationDelay: "1s" }} />
                    </div>
                    <motion.div 
                      className="text-center text-muted-foreground relative z-10"
                      animate={{ scale: [1, 1.02, 1] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <Network className="w-12 h-12 mx-auto mb-3 text-accent" />
                      <div>Network visualization showing key influencers</div>
                      <div className="text-sm mt-2">and content propagation patterns</div>
                    </motion.div>
                  </div>
                  <p className="text-sm text-muted-foreground mt-6 p-4 bg-accent/5 rounded-lg border border-accent/20">
                    Identify key opinion leaders and understand how trends spread through social networks
                  </p>
                </motion.div>
              </TabsContent>

              <TabsContent value="alerts" className="mt-8">
                <motion.div 
                  className="bg-card border-2 border-border rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <h3 className="mb-6">Alert Rules</h3>
                  <div className="space-y-3">
                    {[
                      { title: "Emerging Tech Trends", desc: "Notify when AI/ML topics reach \"Emerging\"", stage: "emerging" as const },
                      { title: "Peak Fashion Alerts", desc: "Alert when fashion clusters hit \"Peaking\"", stage: "peaking" as const },
                      { title: "High Volume Spikes", desc: "Notify on 3x+ engagement increases", stage: "rising" as const },
                    ].map((alert, i) => (
                      <motion.div 
                        key={alert.title}
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-accent/5 to-transparent rounded-xl border border-accent/20 hover:border-accent/40 hover:shadow-md transition-all duration-300 cursor-pointer group"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        whileHover={{ scale: 1.02 }}
                      >
                        <div>
                          <div className="font-medium group-hover:text-accent transition-colors">{alert.title}</div>
                          <div className="text-sm text-muted-foreground">{alert.desc}</div>
                        </div>
                        <TrendBadge stage={alert.stage} />
                      </motion.div>
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mt-6 p-4 bg-accent/5 rounded-lg border border-accent/20">
                    Configure custom rules to receive email or webhook notifications for specific trend patterns
                  </p>
                </motion.div>
              </TabsContent>
            </Tabs>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { title: "Detect", description: "Identify engagement spikes using STL decomposition and z-score analysis", icon: TrendingUp, delay: 0 },
              { title: "Cluster", description: "Group related topics automatically with semantic embeddings", icon: Grid3x3, delay: 0.1 },
              { title: "Predict", description: "Forecast lifecycle stages from emerging to dead", icon: Network, delay: 0.2 },
              { title: "Recommend", description: "Get channel, timing, and content suggestions", icon: Bell, delay: 0.3 },
            ].map((card) => (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: card.delay }}
              >
                <ProductCard
                  title={card.title}
                  description={card.description}
                  icon={card.icon}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}