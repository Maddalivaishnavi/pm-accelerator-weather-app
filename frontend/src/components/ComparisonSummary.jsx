import { buildComparisonTips } from "../lib/comparison";

export default function ComparisonSummary({ home, dest, homeName, destName }) {
  const tips = buildComparisonTips(home, dest, homeName, destName);

  return (
    <div className="comparison-summary">
      <h4>How they compare</h4>
      <ul>
        {tips.map((tip, i) => (
          <li key={i}>{tip}</li>
        ))}
      </ul>
    </div>
  );
}
