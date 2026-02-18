import { Card } from "../ui/card";
import { motion } from "motion/react";
import vedantImage from '../assets/vedantImage.jpeg';


export function About() {
  const founders = [
    {
      name: "Vedant Ladha",
      role: "Co-Founder & CTO",
      image: vedantImage,
    },

    {
      name: "Divij Kathuria",
      role: "Co-Founder & CEO",
    },

    {
      name: "Srijan Gupta",
      role: "Co-Founder & Head of Product",
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
            <h1 className="mb-6">About Trend Radar</h1>
            <p className="text-xl text-muted-foreground">
              We're building the future of social trend intelligence for marketers, creators, and agencies
            </p>
          </motion.div>

          <motion.div 
            className="max-w-[900px] mx-auto mb-20"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div className="prose prose-lg max-w-none">
              <div className="bg-gradient-to-br from-accent/10 to-transparent p-8 rounded-2xl border-2 border-accent/20 mb-12 hover:shadow-lg transition-shadow">
                <h2 className="mb-4">Our Mission</h2>
                <p className="text-muted-foreground">
                  Trend Radar unifies ToS-compliant public signals from platforms like Reddit, X, Instagram Graph API, 
                  TikTok developer surfaces, and licensed blogs/news to detect social-trend spikes, cluster topics, 
                  and forecast lifecycle stages. We turn early signals into marketer-friendly recommendations—what to post, 
                  where, and when—with configurable alert rules and influencer insights.
                </p>
              </div>

              <div className="bg-gradient-to-br from-accent/10 to-transparent p-8 rounded-2xl border-2 border-accent/20 hover:shadow-lg transition-shadow">
                <h2 className="mb-4">Our Approach</h2>
                <p className="text-muted-foreground">
                  Our MVP architecture covers official API ingestion, ETL processing with Polars and DuckDB, 
                  and a comprehensive feature store. We employ proven models for spike detection (STL + z-score), 
                  topic clustering (e5 embeddings + HDBSCAN), and lifecycle tracking through a Finite State Machine. 
                  FastAPI powers our backend while Next.js delivers an intuitive frontend experience.
                </p>
              </div>
            </div>
          </motion.div>

          <div className="mb-20">
            <motion.h2 
              className="text-center mb-12"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              Meet the Team
            </motion.h2>
            <div className="grid md:grid-cols-3 gap-8 max-w-[900px] mx-auto">
              {founders.map((founder, index) => (
                <motion.div
                  key={founder.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -8 }}
                >
                  <Card className="overflow-hidden border-2 hover:border-accent/30 hover:shadow-xl transition-all duration-300 group cursor-pointer">
                    <div className="aspect-square bg-gradient-to-br from-accent/10 to-accent/5 flex items-center justify-center relative overflow-hidden">
                      {/* Animated background circle */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-32 h-32 rounded-full bg-accent/5 group-hover:scale-150 transition-transform duration-500" />
                      </div>
                      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all duration-300 relative z-10">
                        <span className="text-2xl font-semibold text-white">
                          {founder.name.split(" ").map(n => n[0]).join("")}
                        </span>
                      </div>
                    </div>
                    <div className="p-6">
                      <h3 className="mb-1 group-hover:text-accent transition-colors">{founder.name}</h3>
                      <div className="text-sm font-medium text-accent mb-3">{founder.role}</div>
                      <p className="text-sm text-muted-foreground leading-relaxed">{founder.bio}</p>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>

          <motion.div 
            className="bg-gradient-to-br from-muted/50 to-muted/30 rounded-2xl p-8 max-w-[800px] mx-auto text-center border border-border/50 shadow-lg"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h3 className="mb-4">Who We Serve</h3>
            <p className="text-muted-foreground mb-6">
              Our primary users are brand and social marketers, content creators, and marketing agencies 
              who need to stay ahead of trends and maximize their content impact.
            </p>
            <div className="grid md:grid-cols-3 gap-6 text-left">
              {[
                { title: "Brand Marketers", desc: "Plan campaigns around emerging trends before competitors" },
                { title: "Content Creators", desc: "Create viral content by riding trend waves early" },
                { title: "Agencies", desc: "Deliver data-driven insights to multiple clients" },
              ].map((audience, i) => (
                <motion.div
                  key={audience.title}
                  className="p-4 bg-gradient-to-br from-accent/10 to-transparent rounded-xl border border-accent/20 hover:border-accent/40 hover:shadow-md transition-all duration-300 cursor-pointer group"
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <h4 className="mb-2 group-hover:text-accent transition-colors">{audience.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {audience.desc}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}