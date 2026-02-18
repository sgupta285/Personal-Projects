export function Privacy() {
  return (
    <div className="flex-1">
      <section className="max-w-[900px] mx-auto px-6 lg:px-8 py-20">
        <h1 className="mb-8">Privacy Policy</h1>
        
        <div className="prose prose-lg max-w-none space-y-8">
          <div>
            <h2>Data Collection</h2>
            <p className="text-muted-foreground">
              Trend Radar collects public social media signals exclusively through official, ToS-compliant APIs. 
              We do not collect private user data, personal identifiable information (PII), or engage in any form 
              of web scraping or unauthorized data access.
            </p>
          </div>

          <div>
            <h2>How We Use Data</h2>
            <p className="text-muted-foreground">
              Collected public signals are processed to identify trends, cluster topics, and generate recommendations. 
              Data is aggregated and anonymized for trend analysis. We do not sell individual user data or personal 
              information to third parties.
            </p>
          </div>

          <div>
            <h2>Data Sources</h2>
            <p className="text-muted-foreground">
              We access data from the following sources using their official APIs:
            </p>
            <ul className="text-muted-foreground list-disc pl-6 space-y-2">
              <li>Reddit API (public posts and comments)</li>
              <li>X API (public tweets and engagement metrics)</li>
              <li>Instagram Graph API (public business accounts)</li>
              <li>TikTok Business API (public content metrics)</li>
              <li>Licensed news and blog feeds</li>
            </ul>
          </div>

          <div>
            <h2>Data Retention</h2>
            <p className="text-muted-foreground">
              Public trend data is retained according to your subscription tier (7-30 days for standard tiers, 
              custom retention for Enterprise). When content is deleted from source platforms, we purge it from 
              our systems within 24 hours.
            </p>
          </div>

          <div>
            <h2>User Rights</h2>
            <p className="text-muted-foreground">
              Users can request deletion of specific trends or topics from their workspace. Enterprise customers 
              can configure custom data retention policies. We honor all GDPR, CCPA, and platform-specific 
              privacy requirements.
            </p>
          </div>

          <div>
            <h2>Security</h2>
            <p className="text-muted-foreground">
              All data is encrypted in transit (TLS) and at rest. Access is controlled through role-based 
              permissions. We conduct regular security audits and maintain SOC 2 compliance standards.
            </p>
          </div>

          <div>
            <h2>Cookies and Tracking</h2>
            <p className="text-muted-foreground">
              Our website uses essential cookies for authentication and session management. We use analytics 
              to improve our service but do not engage in cross-site tracking or targeted advertising.
            </p>
          </div>

          <div>
            <h2>Third-Party Services</h2>
            <p className="text-muted-foreground">
              We use trusted third-party services for infrastructure (cloud hosting), analytics, and 
              communication. All third parties are required to maintain equivalent privacy and security standards.
            </p>
          </div>

          <div>
            <h2>Updates to This Policy</h2>
            <p className="text-muted-foreground">
              We may update this privacy policy as our services evolve. Material changes will be communicated 
              via email to all active users at least 30 days before taking effect.
            </p>
          </div>

          <div>
            <h2>Contact</h2>
            <p className="text-muted-foreground">
              Questions about our privacy practices? Contact us at privacy@aitrendradar.com
            </p>
          </div>

          <div className="pt-8 border-t border-border text-sm text-muted-foreground">
            <p>Last updated: September 30, 2025</p>
          </div>
        </div>
      </section>
    </div>
  );
}