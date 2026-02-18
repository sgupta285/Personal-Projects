import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";

export function FAQ() {
  const faqs = [
    {
      question: "How do you ensure ToS compliance?",
      answer: "We exclusively use official, developer-approved APIs from each platform (Reddit API, X API, Instagram Graph API, TikTok Business API). We never scrape, violate rate limits, or access private data. All data collection adheres to each platform's Terms of Service and developer agreements.",
    },
    {
      question: "What data sources do you monitor?",
      answer: "We monitor public signals from Reddit, X (Twitter), Instagram (via Graph API), TikTok (via official developer surfaces), and licensed blog/news feeds. Each source is accessed through official APIs with proper authentication and rate limiting.",
    },
    {
      question: "How does Instagram PCAA gating work?",
      answer: "Instagram's Platform Capability Access Assessment (PCAA) requires approval for certain API access levels. We handle this compliance on our end. Depending on your tier, you may have access to basic Instagram insights or advanced features pending PCAA approval.",
    },
    {
      question: "What are your API rate limits?",
      answer: "Rate limits vary by pricing tier and platform. Starter plans have conservative limits to stay well within platform quotas. Professional and Enterprise tiers include higher limits and priority queuing. We automatically handle rate limiting and retry logic to ensure reliable data collection.",
    },
    {
      question: "How do you handle data deletion and privacy?",
      answer: "We honor all platform deletion requests and GDPR/privacy regulations. When content is deleted from source platforms, we purge it from our systems within 24 hours. Users can also request deletion of specific trends or topics from their workspace at any time.",
    },
    {
      question: "What's your uptime and reliability SLA?",
      answer: "We target 99.5% uptime across all tiers. Enterprise customers receive an SLA guarantee with financial penalties for downtime. Our infrastructure uses redundant systems, automated failover, and continuous monitoring to ensure reliability.",
    },
    {
      question: "How accurate are your trend predictions?",
      answer: "Our models achieve 85%+ precision and 80%+ recall on trend lifecycle predictions, with a typical lead time of 2-5 days before peak. Accuracy varies by vertical and is continuously improving through model retraining and feedback loops.",
    },
    {
      question: "Can I integrate Trend Radar with my existing tools?",
      answer: "Yes! Professional and Enterprise tiers include API access and webhook support. You can integrate with your CMS, social media management tools, analytics platforms, and custom internal systems. We also offer Zapier integration for no-code workflows.",
    },
    {
      question: "How often is data refreshed?",
      answer: "Data is ingested in near real-time with updates every 15-30 minutes depending on platform rate limits. Spike detection runs continuously, clustering updates every hour, and lifecycle forecasts refresh every 4 hours.",
    },
    {
      question: "Do you offer a free trial?",
      answer: "We offer a pilot program for qualified users. Contact our team to discuss your use case and we'll set up a custom trial with access to relevant data sources and features for your needs.",
    },
  ];

  return (
    <div className="flex-1">
      <section className="max-w-[900px] mx-auto px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h1 className="mb-6">Frequently Asked Questions</h1>
          <p className="text-xl text-muted-foreground">
            Everything you need to know about Trend Radar
          </p>
        </div>

        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="text-left">{faq.question}</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>

        <div className="mt-16 p-8 bg-muted/30 rounded-lg text-center">
          <h3 className="mb-4">Still have questions?</h3>
          <p className="text-muted-foreground mb-6">
            Our team is here to help. Reach out and we'll get back to you within 24 hours.
          </p>
          <a
            href="mailto:help@trendradar.com"
            className="text-accent hover:underline"
          >
            help@trendradar.com
          </a>
        </div>
      </section>
    </div>
  );
}