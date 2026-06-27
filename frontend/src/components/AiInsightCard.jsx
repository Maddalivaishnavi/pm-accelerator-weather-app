export default function AiInsightCard({ insight }) {
  if (!insight) return null;
  return (
    <section className="ai-insight" aria-label="AI weather summary">
      <span className="ai-insight-badge">AI summary</span>
      <p>{insight}</p>
    </section>
  );
}
