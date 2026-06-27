export default function RecommendationsList({ tips }) {
  if (!tips?.length) return null;
  return (
    <section className="recommendations" aria-label="Recommendations">
      <h3 className="recommendations-title">Worth knowing before you head out</h3>
      <ul>
        {tips.map((tip, i) => (
          <li key={i}>{tip}</li>
        ))}
      </ul>
    </section>
  );
}
