export function Terms() {
  return (
    <div className="flex-1">
      <section className="max-w-[900px] mx-auto px-6 lg:px-8 py-20">
        <h1 className="mb-8">Terms of Service</h1>
        
        <div className="prose prose-lg max-w-none space-y-8">
          <div>
            <h2>Acceptance of Terms</h2>
            <p className="text-muted-foreground">
              By accessing and using Trend Radar, you accept and agree to be bound by these Terms of Service. 
              If you do not agree to these terms, please do not use our service.
            </p>
          </div>

          <div>
            <h2>Service Description</h2>
            <p className="text-muted-foreground">
              Trend Radar provides trend detection, clustering, and lifecycle forecasting based on public 
              social media signals. We deliver insights through our web application, API, and alert systems.
            </p>
          </div>

          <div>
            <h2>Permitted Use</h2>
            <p className="text-muted-foreground">
              You may use our service for:
            </p>
            <ul className="text-muted-foreground list-disc pl-6 space-y-2">
              <li>Marketing and content strategy planning</li>
              <li>Trend research and analysis</li>
              <li>Client reporting and insights (agencies)</li>
              <li>Integration with your own tools and workflows</li>
            </ul>
          </div>

          <div>
            <h2>Prohibited Use</h2>
            <p className="text-muted-foreground">
              You may not:
            </p>
            <ul className="text-muted-foreground list-disc pl-6 space-y-2">
              <li>Resell or redistribute our data without authorization</li>
              <li>Attempt to reverse engineer or circumvent our systems</li>
              <li>Use the service for illegal, harmful, or abusive purposes</li>
              <li>Violate platform ToS by misusing insights</li>
              <li>Share account credentials or exceed seat limits</li>
            </ul>
          </div>

          <div>
            <h2>Data Compliance</h2>
            <p className="text-muted-foreground">
              All data provided through our service is collected via ToS-compliant official APIs. Users are 
              responsible for ensuring their use of insights complies with all applicable laws and platform 
              policies.
            </p>
          </div>

          <div>
            <h2>API Usage</h2>
            <p className="text-muted-foreground">
              API access is subject to rate limits based on your subscription tier. Exceeding limits may result 
              in throttling or temporary suspension. API keys must be kept confidential and not shared publicly.
            </p>
          </div>

          <div>
            <h2>Payment and Billing</h2>
            <p className="text-muted-foreground">
              Subscriptions are billed according to your chosen plan. All fees are non-refundable except as 
              required by law. We reserve the right to modify pricing with 30 days notice to existing customers.
            </p>
          </div>

          <div>
            <h2>Account Termination</h2>
            <p className="text-muted-foreground">
              We reserve the right to suspend or terminate accounts that violate these terms, engage in abusive 
              behavior, or fail to pay. You may cancel your subscription at any time with access continuing 
              through the end of your billing period.
            </p>
          </div>

          <div>
            <h2>Service Availability</h2>
            <p className="text-muted-foreground">
              We strive for 99.5% uptime but do not guarantee uninterrupted service. Maintenance windows will 
              be announced in advance when possible. We are not liable for service interruptions caused by 
              third-party platforms or force majeure events.
            </p>
          </div>

          <div>
            <h2>Intellectual Property</h2>
            <p className="text-muted-foreground">
              Trend Radar retains all rights to our technology, algorithms, and platform. Insights and 
              recommendations generated for your account may be used in your business activities. Raw social 
              data remains subject to source platform terms.
            </p>
          </div>

          <div>
            <h2>Limitation of Liability</h2>
            <p className="text-muted-foreground">
              Trend Radar provides trend intelligence on an "as-is" basis. We are not liable for business 
              decisions made based on our insights, missed trends, or inaccuracies in predictions. Maximum 
              liability is limited to fees paid in the prior 12 months.
            </p>
          </div>

          <div>
            <h2>Changes to Terms</h2>
            <p className="text-muted-foreground">
              We may update these terms as our service evolves. Material changes will be communicated via email 
              at least 30 days before taking effect. Continued use after changes constitutes acceptance.
            </p>
          </div>

          <div>
            <h2>Contact and Disputes</h2>
            <p className="text-muted-foreground">
              Questions about these terms? Contact legal@aitrendradar.com. Disputes shall be resolved through 
              binding arbitration in accordance with the laws of [jurisdiction].
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