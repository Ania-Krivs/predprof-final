export function mapClassificationResponse(response) {
  const predictions = Object.entries(response.all_predictions || {})
    .map(([label, value]) => ({ label, confidence: Number(value) }))
    .sort((a, b) => b.confidence - a.confidence);

  return {
    civilization: response.civilization,
    confidence: Number(response.confidence || 0),
    classId: Number(response.class_id),
    predictions
  };
}
